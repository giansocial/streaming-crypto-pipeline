import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

COINS = [
    "bitcoin",
    "ethereum",
    "solana",
    "cardano",
    "ripple",
    "polkadot",
    "avalanche-2",
    "chainlink",
    "litecoin",
    "uniswap",
]

COIN_LABELS = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "solana": "SOL",
    "cardano": "ADA",
    "ripple": "XRP",
    "polkadot": "DOT",
    "avalanche-2": "AVAX",
    "chainlink": "LINK",
    "litecoin": "LTC",
    "uniswap": "UNI",
}

VS_CURRENCY = "usd"

MARKET_URL = f"{COINGECKO_BASE_URL}/coins/markets"
HISTORY_URL = f"{COINGECKO_BASE_URL}/coins/{{coin_id}}/market_chart"

POLLING_INTERVAL = int(os.environ.get("POLLING_INTERVAL", 60))

VOLATILITY_WINDOW = 30
CORRELATION_MIN_PERIODS = 14
DOMINANCE_THRESHOLD = 0.4

DB_PATH = DATA_DIR / "crypto_market.db"
