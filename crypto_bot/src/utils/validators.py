from __future__ import annotations

"""Validation helpers for various parts of the project."""

from typing import Dict, Any, Tuple


def validate_trading_pair_symbol(symbol: str) -> bool:
    """Validate that ``symbol`` is an uppercase alphanumeric trading pair."""

    return symbol.isalnum() and symbol.upper() == symbol


def extract_base_quote_assets(symbol: str) -> Tuple[str, str]:
    """Extract base and quote assets from ``symbol`` (e.g. ``BTCUSDT``)."""

    if len(symbol) < 6:
        raise ValueError("Symbol too short")
    base = symbol[:-4]
    quote = symbol[-4:]
    return base, quote


def normalize_trading_symbol(symbol: str) -> str:
    """Normalize trading symbol to upper case without spaces."""

    return symbol.replace("/", "").upper()


def validate_processing_time(time_ms: int, target_ms: int) -> bool:
    """Check if ``time_ms`` is within ``target_ms``."""

    return time_ms <= target_ms


def validate_real_time_config(config: Dict[str, Any]) -> bool:
    """Basic validation for real-time configuration dictionary."""

    required = ["enabled"]
    return all(key in config for key in required)


def validate_performance_metrics(metrics: Dict[str, Any]) -> bool:
    """Ensure that provided metrics contain time measurements."""

    return "time_ms" in metrics


def validate_timeframe(timeframe: str) -> bool:
    """Validate Binance timeframe strings like ``1m`` or ``1h``."""

    return timeframe[:-1].isdigit() and timeframe[-1] in {"m", "h", "d"}


def validate_price(price: float) -> bool:
    """Ensure that ``price`` is positive."""

    return price > 0


def validate_rsi_value(value: float) -> bool:
    """RSI must be between 0 and 100."""

    return 0 <= value <= 100


def validate_binance_kline_data_detailed(data: Dict[str, Any]) -> bool:
    """Very light validation for Binance kline websocket message."""

    required_keys = {"t", "T", "o", "c", "h", "l", "v", "x"}
    return required_keys.issubset(data.keys())
