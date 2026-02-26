import json
import pytest
from unittest.mock import patch, MagicMock
from src.extract.coingecko_client import (
    fetch_market_data, parse_market_response, parse_history_response,
)


@pytest.fixture
def sample_market_data():
    with open("tests/fixtures/market_sample.json") as f:
        return json.load(f)


@pytest.fixture
def sample_history_data():
    base_ts = 1715000000000
    return {
        "prices": [
            [base_ts, 67000.0],
            [base_ts + 86400000, 67500.0],
            [base_ts + 172800000, 68200.0],
        ],
        "total_volumes": [
            [base_ts, 28000000000],
            [base_ts + 86400000, 29000000000],
            [base_ts + 172800000, 27000000000],
        ],
        "market_caps": [
            [base_ts, 1300000000000],
            [base_ts + 86400000, 1320000000000],
            [base_ts + 172800000, 1340000000000],
        ],
    }


def test_parse_market_response(sample_market_data):
    df = parse_market_response(sample_market_data)
    assert len(df) == 3
    assert list(df["coin_id"]) == ["bitcoin", "ethereum", "solana"]
    assert df["symbol"].iloc[0] == "BTC"
    assert df["price_usd"].iloc[0] == 67500.0


def test_parse_history_response(sample_history_data):
    df = parse_history_response("bitcoin", sample_history_data)
    assert len(df) == 3
    assert "date" in df.columns
    assert df["price_usd"].iloc[1] == 67500.0
    assert df["volume_24h"].iloc[0] == 28000000000


def test_fetch_market_data_retry():
    mock_resp = MagicMock()
    mock_resp.json.return_value = [{"id": "bitcoin", "symbol": "btc"}]
    mock_resp.raise_for_status.return_value = None

    with patch("src.extract.coingecko_client.requests.get") as mock_get:
        from requests.exceptions import ConnectionError
        mock_get.side_effect = [ConnectionError(), mock_resp]
        result = fetch_market_data(coin_ids=["bitcoin"], max_retries=2)
        assert result == [{"id": "bitcoin", "symbol": "btc"}]
        assert mock_get.call_count == 2


def test_parse_empty_history():
    df = parse_history_response("bitcoin", {"prices": [], "total_volumes": [], "market_caps": []})
    assert df.empty
