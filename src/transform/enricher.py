import numpy as np
import pandas as pd
from src.config.settings import (
    VOLATILITY_WINDOW,
    CORRELATION_MIN_PERIODS,
    DOMINANCE_THRESHOLD,
)


def daily_returns(df):
    if df.empty or "price_usd" not in df.columns:
        return df

    result = df.copy()
    result = result.sort_values(["coin_id", "date"])
    result["daily_return"] = result.groupby("coin_id")["price_usd"].pct_change()
    return result


def rolling_volatility(df, window=None):
    w = window or VOLATILITY_WINDOW
    if df.empty or "daily_return" not in df.columns:
        return df

    result = df.copy()
    result["volatility"] = (
        result.groupby("coin_id")["daily_return"]
        .transform(lambda x: x.rolling(w, min_periods=max(1, w // 2)).std())
    )
    return result


def market_dominance(df):
    if df.empty or "market_cap" not in df.columns:
        return df

    result = df.copy()
    total_cap = result.groupby("date")["market_cap"].transform("sum")
    result["dominance"] = np.where(
        total_cap > 0,
        result["market_cap"] / total_cap,
        0,
    )
    result["is_dominant"] = result["dominance"] >= DOMINANCE_THRESHOLD
    return result


def price_correlation_matrix(df, min_periods=None):
    mp = min_periods or CORRELATION_MIN_PERIODS
    if df.empty:
        return pd.DataFrame()

    pivot = df.pivot_table(
        index="date", columns="coin_id", values="price_usd"
    )
    return pivot.corr(min_periods=mp)


def volume_price_ratio(df):
    if df.empty:
        return df

    result = df.copy()
    result["vp_ratio"] = np.where(
        result["price_usd"] > 0,
        result["volume_24h"] / result["price_usd"],
        0,
    )
    return result


def detect_pumps(df, threshold=0.15):
    if df.empty or "daily_return" not in df.columns:
        return df

    result = df.copy()
    result["is_pump"] = result["daily_return"] > threshold
    result["is_dump"] = result["daily_return"] < -threshold
    return result


def ath_distance(snapshot_df):
    if snapshot_df.empty:
        return snapshot_df

    result = snapshot_df.copy()
    result["ath_distance_pct"] = np.where(
        result["ath"] > 0,
        ((result["price_usd"] - result["ath"]) / result["ath"]) * 100,
        0,
    )
    return result
