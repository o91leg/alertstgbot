from __future__ import annotations

"""Performance measurement helpers."""

from typing import Any, Callable, Dict, List, TypeVar
import asyncio

import structlog

from .time_helpers import get_high_precision_timestamp, get_time_since_ms

T = TypeVar("T")


class TimingContext:
    """Context manager measuring execution time in milliseconds."""

    def __init__(self, operation: str, target_ms: int | None = None) -> None:
        self.operation = operation
        self.target_ms = target_ms

    def __enter__(self) -> "TimingContext":
        self.start = get_high_precision_timestamp()
        self.elapsed_ms = 0
        return self

    def __exit__(self, *exc: Any) -> None:  # noqa: D401 - short
        self.elapsed_ms = get_time_since_ms(self.start)
        self.is_within_target = (
            self.target_ms is None or self.elapsed_ms <= self.target_ms
        )


def measure_time(target_ms: int | None = None) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator that measures function execution time.

    The elapsed time in milliseconds is stored on the returned function as
    ``last_elapsed_ms``.  ``target_ms`` is kept for potential external checks.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        if asyncio.iscoroutinefunction(func):

            async def async_wrapper(*args: Any, **kwargs: Any) -> T:
                start = get_high_precision_timestamp()
                result = await func(*args, **kwargs)
                async_wrapper.last_elapsed_ms = get_time_since_ms(start)  # type: ignore[attr-defined]
                return result

            async_wrapper.target_ms = target_ms  # type: ignore[attr-defined]
            return async_wrapper  # type: ignore[return-value]

        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            start = get_high_precision_timestamp()
            result = func(*args, **kwargs)
            sync_wrapper.last_elapsed_ms = get_time_since_ms(start)  # type: ignore[attr-defined]
            return result

        sync_wrapper.target_ms = target_ms  # type: ignore[attr-defined]
        return sync_wrapper

    return decorator


def log_slow_operations(target_ms: int) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator logging when execution time exceeds ``target_ms``."""

    logger = structlog.get_logger("performance")

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        if asyncio.iscoroutinefunction(func):

            async def async_wrapper(*args: Any, **kwargs: Any) -> T:
                start = get_high_precision_timestamp()
                result = await func(*args, **kwargs)
                elapsed = get_time_since_ms(start)
                if elapsed > target_ms:
                    logger.warning("slow_operation", function=func.__name__, time_ms=elapsed)
                return result

            return async_wrapper  # type: ignore[return-value]

        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            start = get_high_precision_timestamp()
            result = func(*args, **kwargs)
            elapsed = get_time_since_ms(start)
            if elapsed > target_ms:
                logger.warning("slow_operation", function=func.__name__, time_ms=elapsed)
            return result

        return sync_wrapper

    return decorator


_MONITOR_DATA: Dict[str, List[int]] = {}


def monitor_real_time_performance(operation: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator collecting execution times for ``operation``."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        if asyncio.iscoroutinefunction(func):

            async def async_wrapper(*args: Any, **kwargs: Any) -> T:
                start = get_high_precision_timestamp()
                result = await func(*args, **kwargs)
                elapsed = int(get_time_since_ms(start))
                _MONITOR_DATA.setdefault(operation, []).append(elapsed)
                return result

            return async_wrapper  # type: ignore[return-value]

        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            start = get_high_precision_timestamp()
            result = func(*args, **kwargs)
            elapsed = int(get_time_since_ms(start))
            _MONITOR_DATA.setdefault(operation, []).append(elapsed)
            return result

        return sync_wrapper

    return decorator


def create_performance_alert(operation: str, time_ms: int, target_ms: int) -> Dict[str, Any]:
    """Return structured alert information."""

    return {
        "operation": operation,
        "time_ms": time_ms,
        "target_ms": target_ms,
        "is_within_target": time_ms <= target_ms,
    }


def detect_performance_regression(history: List[int], new_time: int) -> bool:
    """Check if ``new_time`` is slower than historical average."""

    if not history:
        return False
    avg = sum(history) / len(history)
    return new_time > avg


def generate_performance_summary() -> Dict[str, Any]:
    """Return aggregated performance metrics for monitored operations."""

    summary: Dict[str, Any] = {}
    for op, values in _MONITOR_DATA.items():
        if not values:
            continue
        avg = sum(values) / len(values)
        summary[op] = {"avg_ms": avg, "max_ms": max(values)}
    return summary
