from __future__ import annotations

"""Various mathematical helper utilities."""

from typing import Iterable, List, Sequence


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers returning ``default`` on zero denominator."""

    try:
        return numerator / denominator
    except ZeroDivisionError:
        return default


def calculate_percentage_change(current: float, previous: float) -> float:
    """Return percentage change between ``current`` and ``previous`` values."""

    if previous == 0:
        return 0.0
    return (current - previous) / abs(previous) * 100


def round_to_precision(value: float, precision: int) -> float:
    """Round ``value`` to ``precision`` decimal places."""

    return round(value, precision)


def calculate_performance_score(target_ms: int, actual_ms: int) -> float:
    """Return actual/target ratio (1.0 == meets target)."""

    if target_ms <= 0:
        return 0.0
    return actual_ms / target_ms


def detect_performance_degradation(history: Sequence[int], threshold: float) -> bool:
    """Check if average in ``history`` exceeds ``threshold``."""

    if not history:
        return False
    return sum(history) / len(history) > threshold


def calculate_moving_average_performance(values: Sequence[int], window: int) -> float:
    """Calculate moving average over ``window`` values."""

    if not values:
        return 0.0
    window_values = values[-window:]
    return sum(window_values) / len(window_values)


def calculate_simple_moving_average(prices: Sequence[float], period: int) -> float | None:
    """Simple moving average of ``prices`` if enough data is available."""

    if len(prices) < period:
        return None
    return sum(prices[-period:]) / period
