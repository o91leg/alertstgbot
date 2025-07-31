from __future__ import annotations

"""Helpers for working with timestamps and timeframes."""

from datetime import datetime, timedelta, timezone
from typing import Callable, TypeVar, Any
import asyncio
import time

F = TypeVar("F", bound=Callable[..., Any])


def get_high_precision_timestamp() -> int:
    """Return high precision timestamp in nanoseconds."""

    return time.perf_counter_ns()


def get_time_since_ms(start_ns: int) -> int:
    """Return milliseconds elapsed since ``start_ns``."""

    return int((time.perf_counter_ns() - start_ns) / 1_000_000)


def is_within_time_target(start_ns: int, target_ms: int) -> bool:
    """Check if the elapsed time since ``start_ns`` is within ``target_ms``."""

    return get_time_since_ms(start_ns) <= target_ms


def timeframe_to_milliseconds(timeframe: str) -> int:
    """Convert Binance timeframe string (e.g. ``1m``) to milliseconds."""

    unit = timeframe[-1]
    value = int(timeframe[:-1])
    if unit == "m":
        return value * 60_000
    if unit == "h":
        return value * 3_600_000
    if unit == "d":
        return value * 86_400_000
    raise ValueError(f"Unsupported timeframe: {timeframe}")


def align_timestamp_to_timeframe(timestamp_ms: int, timeframe: str) -> int:
    """Align ``timestamp_ms`` down to the beginning of the timeframe."""

    tf_ms = timeframe_to_milliseconds(timeframe)
    return timestamp_ms - (timestamp_ms % tf_ms)


def calculate_time_until_next_candle(current_ms: int, timeframe: str) -> int:
    """Return milliseconds until the next candle for ``timeframe``."""

    tf_ms = timeframe_to_milliseconds(timeframe)
    return tf_ms - (current_ms % tf_ms)


def timestamp_to_datetime(timestamp_ms: int) -> datetime:
    """Convert milliseconds timestamp to timezone-aware ``datetime``."""

    return datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)


def measure_execution_time(func: F) -> F:
    """Decorator measuring execution time and returning result and time in ms."""

    if asyncio.iscoroutinefunction(func):  # type: ignore[attr-defined]
        async def wrapper(*args: Any, **kwargs: Any):
            start = get_high_precision_timestamp()
            result = await func(*args, **kwargs)
            return result, get_time_since_ms(start)

        return wrapper  # type: ignore[return-value]

    def sync_wrapper(*args: Any, **kwargs: Any):
        start = get_high_precision_timestamp()
        result = func(*args, **kwargs)
        return result, get_time_since_ms(start)

    return sync_wrapper  # type: ignore[return-value]
