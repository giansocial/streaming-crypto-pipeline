import time
import requests
import pandas as pd
from src.config.settings import MARKET_URL, HISTORY_URL, VS_CURRENCY, COINS


def fetch_market_data(coin_ids=None, max_retries=3):
    coins = coin_ids or COINS
    params = {
        "vs_currency": VS_CURRENCY,
        "ids": ",".join(coins),
        "order": "market_cap_desc",
        "per_page": len(coins),
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "24h,7d,30d",
    }

    for attempt in range(max_retries):
        try:
            resp = requests.get(MARKET_URL, params=params, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise


def parse_market_response(raw_data):
    records = []
    for coin in raw_data:
        records.append({
            "coin_id": coin["id"],
            "symbol": coin["symbol"].upper(),
            "name": coin["name"],
            "price_usd": coin.get("current_price"),
            "market_cap": coin.get("market_cap"),
            "volume_24h": coin.get("total_volume"),
            "change_24h_pct": coin.get("price_change_percentage_24h"),
            "change_7d_pct": coin.get("price_change_percentage_7d_in_currency"),
            "change_30d_pct": coin.get("price_change_percentage_30d_in_currency"),
            "circulating_supply": coin.get("circulating_supply"),
            "total_supply": coin.get("total_supply"),
            "ath": coin.get("ath"),
            "ath_date": coin.get("ath_date"),
            "last_updated": coin.get("last_updated"),
        })
    return pd.DataFrame(records)


def fetch_price_history(coin_id, days=90, max_retries=3):
    url = HISTORY_URL.format(coin_id=coin_id)
    params = {
        "vs_currency": VS_CURRENCY,
        "days": days,
        "interval": "daily",
    }

    for attempt in range(max_retries):
        try:
            resp = requests.get(url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return parse_history_response(coin_id, data)
        except requests.RequestException:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise


def parse_history_response(coin_id, data):
    prices = data.get("prices", [])
    volumes = data.get("total_volumes", [])
    caps = data.get("market_caps", [])

    records = []
    for i, (ts, price) in enumerate(prices):
        record = {
            "coin_id": coin_id,
            "timestamp": pd.Timestamp(ts, unit="ms"),
            "price_usd": price,
        }
        if i < len(volumes):
            record["volume_24h"] = volumes[i][1]
        if i < len(caps):
            record["market_cap"] = caps[i][1]
        records.append(record)

    df = pd.DataFrame(records)
    if not df.empty:
        df["date"] = df["timestamp"].dt.date
    return df
