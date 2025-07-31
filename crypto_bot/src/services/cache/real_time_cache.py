from __future__ import annotations

"""Lightweight cache for real-time metrics and prices."""

import json
from typing import Any, Dict

from redis.asyncio import Redis


class RealTimeCache:
    """Short-lived cache for high frequency data."""

    def __init__(self, redis: Redis, price_ttl: int = 10, metrics_ttl: int = 60) -> None:
        self.redis = redis
        self.price_ttl = price_ttl
        self.metrics_ttl = metrics_ttl

    async def set_current_price(self, symbol: str, price: float) -> None:
        await self.redis.set(f"price:{symbol}", price, ex=self.price_ttl)

    async def get_current_price(self, symbol: str) -> float | None:
        value = await self.redis.get(f"price:{symbol}")
        return float(value) if value is not None else None

    async def set_processing_metrics(self, symbol: str, metrics: Dict[str, Any]) -> None:
        key = f"metrics:{symbol}"
        await self.redis.set(key, json.dumps(metrics), ex=self.metrics_ttl)

    async def increment_processing_counter(self, symbol: str) -> int:
        key = f"counter:{symbol}"
        value = await self.redis.incr(key)
        await self.redis.expire(key, self.metrics_ttl)
        return int(value)

    async def set_performance_alert(self, symbol: str, alert: str) -> None:
        await self.redis.set(f"alert:{symbol}", alert, ex=self.metrics_ttl)

    async def cleanup_old_metrics(self) -> None:
        # Placeholder for potential cleanup logic.
        return None
