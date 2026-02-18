import numpy as np


def validate_prices(df):
    if df.empty:
        return {"score": 0, "issues": ["empty dataframe"]}

    issues = []
    total_rows = len(df)

    null_prices = df["price_usd"].isna().sum()
    if null_prices > 0:
        issues.append(f"{null_prices} null prices")

    negative = (df["price_usd"] < 0).sum()
    if negative > 0:
        issues.append(f"{negative} negative prices")

    completeness = 1 - (null_prices / total_rows) if total_rows > 0 else 0
    validity = 1 - (negative / total_rows) if total_rows > 0 else 0

    score = round((completeness * 0.6 + validity * 0.4) * 100, 1)
    return {"score": score, "issues": issues}


def validate_market_caps(df):
    if df.empty:
        return {"score": 0, "issues": ["empty dataframe"]}

    issues = []
    total = len(df)

    null_caps = df["market_cap"].isna().sum()
    if null_caps > 0:
        issues.append(f"{null_caps} null market caps")

    if "volume_24h" in df.columns:
        suspicious = (df["volume_24h"] > df["market_cap"] * 10).sum()
        if suspicious > 0:
            issues.append(f"{suspicious} coins with volume > 10x market cap")

    completeness = 1 - (null_caps / total) if total > 0 else 0
    score = round(completeness * 100, 1)
    return {"score": score, "issues": issues}


def validate_temporal_coverage(df, expected_days=90):
    if df.empty or "date" not in df.columns:
        return {"score": 0, "issues": ["no temporal data"]}

    issues = []
    coins = df["coin_id"].unique()
    coverage_scores = []

    for coin in coins:
        coin_df = df[df["coin_id"] == coin]
        actual_days = coin_df["date"].nunique()
        ratio = min(actual_days / expected_days, 1.0)
        coverage_scores.append(ratio)

        if ratio < 0.8:
            issues.append(f"{coin}: only {actual_days}/{expected_days} days")

    avg_coverage = np.mean(coverage_scores) if coverage_scores else 0
    score = round(avg_coverage * 100, 1)
    return {"score": score, "issues": issues}
