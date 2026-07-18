import argparse
import time
from datetime import datetime

from src.extract.coingecko_client import fetch_market_data, parse_market_response, fetch_price_history
from src.transform.cleaner import clean_market_snapshot, clean_price_history
from src.transform.enricher import (
    daily_returns, rolling_volatility, market_dominance,
    detect_pumps, ath_distance, volume_price_ratio, price_correlation_matrix,
)
from src.quality.validators import validate_prices, validate_market_caps
from src.load.warehouse import get_connection, create_tables, upsert_coins, insert_snapshots, upsert_history
from src.utils.logger import get_logger
from src.config.settings import POLLING_INTERVAL

logger = get_logger("pipeline")


def run_snapshot(conn):
    logger.info("fetching market snapshot")
    raw = fetch_market_data()
    df = parse_market_response(raw)
    df = clean_market_snapshot(df)

    price_check = validate_prices(df)
    cap_check = validate_market_caps(df)
    logger.info(f"quality - prices: {price_check['score']}, caps: {cap_check['score']}")

    df = ath_distance(df)
    df["captured_at"] = datetime.utcnow().isoformat()

    coins = upsert_coins(conn, df)
    snaps = insert_snapshots(conn, df)
    logger.info(f"snapshot: {coins} coins, {snaps} records")
    return {"coins": coins, "snapshots": snaps, "quality": price_check}


def run_history(conn, coins=None, days=90):
    logger.info(f"fetching {days}-day history")
    from src.config.settings import COINS
    target_coins = coins or COINS

    all_history = []
    for coin_id in target_coins:
        try:
            df = fetch_price_history(coin_id, days=days)
            all_history.append(df)
            time.sleep(1.5)
        except Exception as e:
            logger.warning(f"failed to fetch {coin_id}: {e}")

    if not all_history:
        return {"records": 0}

    import pandas as pd
    combined = pd.concat(all_history, ignore_index=True)
    combined = clean_price_history(combined)
    combined = daily_returns(combined)
    combined = rolling_volatility(combined)
    combined = market_dominance(combined)
    combined = volume_price_ratio(combined)
    combined = detect_pumps(combined)
    correlation = price_correlation_matrix(combined)

    records = upsert_history(conn, combined)
    logger.info(f"history: {records} records loaded")
    return {"records": records, "correlation": correlation}


def run_pipeline(mode="snapshot", days=90, loop=False, interval=60):
    conn = get_connection()
    create_tables(conn)

    try:
        if mode == "snapshot":
            result = run_snapshot(conn)
        elif mode == "history":
            result = run_history(conn, days=days)
        elif mode == "full":
            snap = run_snapshot(conn)
            hist = run_history(conn, days=days)
            result = {**snap, **hist}
        else:
            raise ValueError(f"unknown mode: {mode}")

        if loop and mode == "snapshot":
            logger.info(f"loop mode, polling every {interval}s")
            while True:
                time.sleep(interval)
                run_snapshot(conn)
        return result
    finally:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="snapshot", choices=["snapshot", "history", "full"])
    parser.add_argument("--days", type=int, default=90)
    parser.add_argument("--loop", action="store_true")
    parser.add_argument("--interval", type=int, default=POLLING_INTERVAL)
    args = parser.parse_args()

    run_pipeline(
        mode=args.mode,
        days=args.days,
        loop=args.loop,
        interval=args.interval,
    )
