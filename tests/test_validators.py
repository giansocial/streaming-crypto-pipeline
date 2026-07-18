import pandas as pd
from src.quality.validators import validate_prices, validate_market_caps, validate_temporal_coverage


def test_validate_prices_clean():
    df = pd.DataFrame({
        "price_usd": [67500.0, 3200.0, 145.0],
        "market_cap": [1.3e12, 3.85e11, 6.3e10],
    })
    result = validate_prices(df)
    assert result["score"] == 100.0
    assert result["issues"] == []


def test_validate_prices_with_nulls():
    df = pd.DataFrame({
        "price_usd": [67500.0, None, 145.0],
        "market_cap": [1.3e12, 3.85e11, 6.3e10],
    })
    result = validate_prices(df)
    assert result["score"] < 100
    assert any("null" in i for i in result["issues"])


def test_validate_market_caps_suspicious_volume():
    df = pd.DataFrame({
        "market_cap": [1.3e12, 100],
        "volume_24h": [28e9, 5000],
    })
    result = validate_market_caps(df)
    assert result["score"] == 100.0
    assert any("volume" in i for i in result["issues"])


def test_validate_temporal_coverage():
    dates = pd.date_range("2026-04-01", periods=80).date
    df = pd.DataFrame({
        "coin_id": ["bitcoin"] * 80,
        "date": dates,
    })
    result = validate_temporal_coverage(df, expected_days=90)
    assert result["score"] < 100
    assert result["score"] > 80


def test_validate_empty():
    result = validate_prices(pd.DataFrame())
    assert result["score"] == 0
