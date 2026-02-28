import pandas as pd
import numpy as np
import pytest
from src.transform.enricher import (
    daily_returns, rolling_volatility, market_dominance,
    price_correlation_matrix, detect_pumps, ath_distance,
    volume_price_ratio,
)


@pytest.fixture
def history_df():
    dates = pd.date_range("2026-04-01", periods=10).date
    btc_prices = [67000, 67500, 68000, 66000, 67200, 68500, 69000, 67800, 68200, 69500]
    eth_prices = [3200, 3250, 3300, 3100, 3180, 3350, 3400, 3280, 3320, 3450]
    records = []
    for i, d in enumerate(dates):
        records.append({"coin_id": "bitcoin", "date": d, "price_usd": btc_prices[i],
                        "volume_24h": 28e9, "market_cap": btc_prices[i] * 19.6e6})
        records.append({"coin_id": "ethereum", "date": d, "price_usd": eth_prices[i],
                        "volume_24h": 15e9, "market_cap": eth_prices[i] * 120e6})
    return pd.DataFrame(records)


def test_daily_returns(history_df):
    df = daily_returns(history_df)
    assert "daily_return" in df.columns
    btc = df[df["coin_id"] == "bitcoin"]
    assert pd.isna(btc["daily_return"].iloc[0])
    expected = (67500 - 67000) / 67000
    assert abs(btc["daily_return"].iloc[1] - expected) < 0.0001


def test_rolling_volatility(history_df):
    df = daily_returns(history_df)
    df = rolling_volatility(df, window=5)
    assert "volatility" in df.columns
    non_null = df["volatility"].dropna()
    assert len(non_null) > 0


def test_market_dominance(history_df):
    df = market_dominance(history_df)
    assert "dominance" in df.columns
    btc_dom = df[df["coin_id"] == "bitcoin"]["dominance"]
    assert all(btc_dom > 0.5)


def test_correlation_matrix(history_df):
    corr = price_correlation_matrix(history_df, min_periods=5)
    assert "bitcoin" in corr.columns
    assert "ethereum" in corr.columns
    assert corr.loc["bitcoin", "bitcoin"] == pytest.approx(1.0)


def test_detect_pumps(history_df):
    df = daily_returns(history_df)
    df = detect_pumps(df, threshold=0.01)
    assert "is_pump" in df.columns
    assert "is_dump" in df.columns


def test_ath_distance():
    df = pd.DataFrame({
        "coin_id": ["bitcoin", "ethereum"],
        "price_usd": [67500.0, 3200.0],
        "ath": [73750.0, 4878.26],
    })
    result = ath_distance(df)
    assert result["ath_distance_pct"].iloc[0] < 0
    assert result["ath_distance_pct"].iloc[1] < 0


def test_volume_price_ratio(history_df):
    df = volume_price_ratio(history_df)
    assert "vp_ratio" in df.columns
    assert all(df["vp_ratio"] > 0)
