import pandas as pd


def clean_market_snapshot(df):
    if df.empty:
        return df

    numeric_cols = [
        "price_usd", "market_cap", "volume_24h",
        "change_24h_pct", "change_7d_pct", "change_30d_pct",
        "circulating_supply", "total_supply", "ath",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["price_usd", "market_cap"])

    if "last_updated" in df.columns:
        df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce")

    if "ath_date" in df.columns:
        df["ath_date"] = pd.to_datetime(df["ath_date"], errors="coerce")

    return df.reset_index(drop=True)


def clean_price_history(df):
    if df.empty:
        return df

    df = df.dropna(subset=["price_usd"])
    df = df.drop_duplicates(subset=["coin_id", "date"], keep="last")
    df = df.sort_values(["coin_id", "date"]).reset_index(drop=True)
    return df


def merge_snapshots(existing, new_data):
    if existing.empty:
        return new_data
    if new_data.empty:
        return existing

    combined = pd.concat([existing, new_data], ignore_index=True)
    combined = combined.drop_duplicates(
        subset=["coin_id", "last_updated"], keep="last"
    )
    return combined.sort_values(
        ["coin_id", "last_updated"]
    ).reset_index(drop=True)
