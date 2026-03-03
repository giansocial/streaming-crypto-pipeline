import sqlite3
import pandas as pd
import pytest
from src.load.warehouse import (
    create_tables, upsert_coins, insert_snapshots,
    upsert_history, query_latest_prices,
)


@pytest.fixture
def db_conn(tmp_path):
    db_path = str(tmp_path / "test_crypto.db")
    conn = sqlite3.connect(db_path)
    create_tables(conn)
    yield conn
    conn.close()


@pytest.fixture
def coin_df():
    return pd.DataFrame({
        "coin_id": ["bitcoin", "ethereum"],
        "symbol": ["BTC", "ETH"],
        "name": ["Bitcoin", "Ethereum"],
    })


def test_create_tables(db_conn):
    cursor = db_conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    tables = [row[0] for row in cursor.fetchall()]
    assert "dim_coin" in tables
    assert "market_snapshot" in tables
    assert "price_history" in tables


def test_upsert_coins(db_conn, coin_df):
    count = upsert_coins(db_conn, coin_df)
    assert count == 2
    rows = db_conn.execute("SELECT * FROM dim_coin").fetchall()
    assert len(rows) == 2


def test_insert_snapshots(db_conn, coin_df):
    upsert_coins(db_conn, coin_df)
    snap_df = pd.DataFrame({
        "coin_id": ["bitcoin", "ethereum"],
        "price_usd": [67500.0, 3200.0],
        "market_cap": [1.3e12, 3.85e11],
        "volume_24h": [28e9, 15e9],
        "change_24h_pct": [2.15, -1.2],
        "captured_at": ["2026-05-10T14:30:00", "2026-05-10T14:30:00"],
    })
    count = insert_snapshots(db_conn, snap_df)
    assert count == 2


def test_upsert_history_idempotent(db_conn, coin_df):
    upsert_coins(db_conn, coin_df)
    hist = pd.DataFrame({
        "coin_id": ["bitcoin", "bitcoin"],
        "date": ["2026-05-01", "2026-05-01"],
        "price_usd": [67000.0, 67500.0],
    })
    upsert_history(db_conn, hist)
    rows = db_conn.execute("SELECT * FROM price_history").fetchall()
    assert len(rows) == 1


def test_query_latest_prices(db_conn, coin_df):
    upsert_coins(db_conn, coin_df)
    snap_df = pd.DataFrame({
        "coin_id": ["bitcoin", "ethereum"],
        "price_usd": [67500.0, 3200.0],
        "change_24h_pct": [2.15, -1.2],
        "captured_at": ["2026-05-10T14:30:00", "2026-05-10T14:30:00"],
    })
    insert_snapshots(db_conn, snap_df)
    result = query_latest_prices(db_conn)
    assert len(result) == 2
    assert result["symbol"].iloc[0] == "BTC"
