import sqlite3
import pandas as pd
from src.config.settings import DB_PATH


def get_connection(db_path=None):
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def create_tables(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS dim_coin (
            coin_id TEXT PRIMARY KEY,
            symbol TEXT NOT NULL,
            name TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS market_snapshot (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin_id TEXT NOT NULL,
            price_usd REAL,
            market_cap REAL,
            volume_24h REAL,
            change_24h_pct REAL,
            change_7d_pct REAL,
            change_30d_pct REAL,
            circulating_supply REAL,
            ath REAL,
            ath_distance_pct REAL,
            captured_at TEXT NOT NULL,
            FOREIGN KEY (coin_id) REFERENCES dim_coin(coin_id)
        );

        CREATE TABLE IF NOT EXISTS price_history (
            coin_id TEXT NOT NULL,
            date TEXT NOT NULL,
            price_usd REAL,
            volume_24h REAL,
            market_cap REAL,
            daily_return REAL,
            volatility REAL,
            dominance REAL,
            PRIMARY KEY (coin_id, date),
            FOREIGN KEY (coin_id) REFERENCES dim_coin(coin_id)
        );

        CREATE INDEX IF NOT EXISTS idx_snapshot_coin
            ON market_snapshot(coin_id);
        CREATE INDEX IF NOT EXISTS idx_snapshot_date
            ON market_snapshot(captured_at);
        CREATE INDEX IF NOT EXISTS idx_history_date
            ON price_history(date);
    """)


def upsert_coins(conn, df):
    if df.empty:
        return 0

    coins = df[["coin_id", "symbol", "name"]].drop_duplicates(subset=["coin_id"])
    count = 0
    for _, row in coins.iterrows():
        conn.execute(
            "INSERT OR REPLACE INTO dim_coin (coin_id, symbol, name) VALUES (?, ?, ?)",
            (row["coin_id"], row["symbol"], row["name"]),
        )
        count += 1
    conn.commit()
    return count


def insert_snapshots(conn, df):
    if df.empty:
        return 0

    cols = [
        "coin_id", "price_usd", "market_cap", "volume_24h",
        "change_24h_pct", "change_7d_pct", "change_30d_pct",
        "circulating_supply", "ath", "ath_distance_pct", "captured_at",
    ]
    available = [c for c in cols if c in df.columns]
    records = df[available].to_dict("records")

    placeholders = ", ".join(["?"] * len(available))
    col_names = ", ".join(available)
    sql = f"INSERT INTO market_snapshot ({col_names}) VALUES ({placeholders})"

    count = 0
    for rec in records:
        conn.execute(sql, [rec.get(c) for c in available])
        count += 1
    conn.commit()
    return count


def upsert_history(conn, df):
    if df.empty:
        return 0

    cols = [
        "coin_id", "date", "price_usd", "volume_24h",
        "market_cap", "daily_return", "volatility", "dominance",
    ]
    available = [c for c in cols if c in df.columns]

    placeholders = ", ".join(["?"] * len(available))
    col_names = ", ".join(available)
    sql = f"INSERT OR REPLACE INTO price_history ({col_names}) VALUES ({placeholders})"

    count = 0
    for _, row in df.iterrows():
        conn.execute(sql, [row.get(c) for c in available])
        count += 1
    conn.commit()
    return count


def query_latest_prices(conn):
    sql = """
        SELECT d.symbol, s.price_usd, s.change_24h_pct, s.captured_at
        FROM market_snapshot s
        JOIN dim_coin d ON s.coin_id = d.coin_id
        WHERE s.id IN (
            SELECT MAX(id) FROM market_snapshot GROUP BY coin_id
        )
        ORDER BY s.price_usd DESC
    """
    return pd.read_sql_query(sql, conn)
