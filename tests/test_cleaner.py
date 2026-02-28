import pandas as pd
import pytest
from src.transform.cleaner import clean_market_snapshot, clean_price_history, merge_snapshots


@pytest.fixture
def raw_snapshot():
    return pd.DataFrame({
        "coin_id": ["bitcoin", "ethereum", "solana"],
        "symbol": ["BTC", "ETH", "SOL"],
        "name": ["Bitcoin", "Ethereum", "Solana"],
        "price_usd": [67500.0, 3200.0, None],
        "market_cap": [1325000000000, 385000000000, None],
        "volume_24h": [28000000000, 15000000000, 2800000000],
        "last_updated": ["2026-05-10T14:30:00Z", "2026-05-10T14:30:00Z", None],
    })


def test_clean_removes_null_prices(raw_snapshot):
    df = clean_market_snapshot(raw_snapshot)
    assert len(df) == 2
    assert "solana" not in df["coin_id"].values


def test_clean_converts_types(raw_snapshot):
    df = clean_market_snapshot(raw_snapshot)
    assert df["price_usd"].dtype == float
    assert pd.api.types.is_datetime64_any_dtype(df["last_updated"])


def test_clean_price_history_dedup():
    df = pd.DataFrame({
        "coin_id": ["bitcoin", "bitcoin", "ethereum"],
        "date": ["2026-05-01", "2026-05-01", "2026-05-01"],
        "price_usd": [67000.0, 67500.0, 3200.0],
    })
    result = clean_price_history(df)
    btc = result[result["coin_id"] == "bitcoin"]
    assert len(btc) == 1
    assert btc["price_usd"].iloc[0] == 67500.0


def test_merge_snapshots():
    old = pd.DataFrame({
        "coin_id": ["bitcoin"],
        "price_usd": [67000.0],
        "last_updated": [pd.Timestamp("2026-05-09")],
    })
    new = pd.DataFrame({
        "coin_id": ["bitcoin"],
        "price_usd": [67500.0],
        "last_updated": [pd.Timestamp("2026-05-10")],
    })
    result = merge_snapshots(old, new)
    assert len(result) == 2


def test_clean_empty():
    df = clean_market_snapshot(pd.DataFrame())
    assert df.empty
