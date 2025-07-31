from __future__ import annotations

"""Performance measurement helpers."""

from typing import Any, Callable, TypeVar
import asyncio

from .time_helpers import get_high_precision_timestamp, get_time_since_ms

T = TypeVar("T")


class TimingContext:
    """Context manager measuring execution time in milliseconds."""

    def __enter__(self) -> "TimingContext":
        self.start = get_high_precision_timestamp()
        self.elapsed_ms = 0
        return self

    def __exit__(self, *exc: Any) -> None:  # noqa: D401 - short
        self.elapsed_ms = get_time_since_ms(self.start)


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
