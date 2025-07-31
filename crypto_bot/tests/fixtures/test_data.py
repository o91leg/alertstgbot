from datetime import datetime, timezone
from typing import Any, Dict, List


def get_test_candle_data() -> List[Dict[str, Any]]:
    """Return sample candle data for tests."""
    return [
        {
            "symbol": "BTCUSDT",
            "timeframe": "1m",
            "open_time": datetime.now(timezone.utc),
            "close_time": datetime.now(timezone.utc),
            "open_price": 45000.0,
            "high_price": 45100.0,
            "low_price": 44900.0,
            "close_price": 45050.0,
            "volume": 100.0,
            "is_closed": True,
        }
    ]


def get_test_rsi_prices() -> List[float]:
    """Return prices with known RSI result."""
    return [
        44.34,
        44.09,
        44.15,
        43.61,
        44.33,
        44.83,
        45.85,
        47.80,
        47.37,
        46.80,
        46.47,
        46.27,
        47.15,
        47.77,
        47.72,
        48.39,
    ]


def get_expected_rsi_result() -> float:
    """Expected RSI value for the sample prices."""
    return 73.04
