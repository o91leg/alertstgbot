from __future__ import annotations

"""Caching of indicator values such as RSI and EMA."""

import json
from typing import Any, Dict, Tuple

from redis.asyncio import Redis


class IndicatorCache:
    """Cache for technical indicators."""

    def __init__(self, redis: Redis, ttl: int = 30, state_ttl: int = 300) -> None:
        self.redis = redis
        self.ttl = ttl
        self.state_ttl = state_ttl

    def _rsi_key(self, symbol: str, timeframe: str, period: int) -> str:
        return f"rsi:{symbol}:{timeframe}:{period}"

    def _ema_key(self, symbol: str, timeframe: str, period: int) -> str:
        return f"ema:{symbol}:{timeframe}:{period}"

    def _state_key(self, name: str, symbol: str, timeframe: str) -> str:
        return f"state:{name}:{symbol}:{timeframe}"

    async def get_rsi(self, symbol: str, timeframe: str, period: int) -> float | None:
        value = await self.redis.get(self._rsi_key(symbol, timeframe, period))
        return float(value) if value is not None else None

    async def set_rsi(self, symbol: str, timeframe: str, period: int, value: float) -> None:
        await self.redis.set(self._rsi_key(symbol, timeframe, period), value, ex=self.ttl)

    async def get_ema(self, symbol: str, timeframe: str, period: int) -> float | None:
        value = await self.redis.get(self._ema_key(symbol, timeframe, period))
        return float(value) if value is not None else None

    async def set_ema(self, symbol: str, timeframe: str, period: int, value: float) -> None:
        await self.redis.set(self._ema_key(symbol, timeframe, period), value, ex=self.ttl)

    async def get_rsi_with_previous(
        self, symbol: str, timeframe: str, period: int
    ) -> Tuple[float | None, float | None]:
        """Return current and previous RSI values."""

        key = self._rsi_key(symbol, timeframe, period)
        values = await self.redis.lrange(key, 0, 1)
        if not values:
            return None, None
        current = float(values[0])
        previous = float(values[1]) if len(values) > 1 else None
        return current, previous

    async def save_indicator_state(
        self, name: str, symbol: str, timeframe: str, state: Dict[str, Any]
    ) -> None:
        key = self._state_key(name, symbol, timeframe)
        await self.redis.set(key, json.dumps(state), ex=self.state_ttl)

    async def get_indicator_state(self, name: str, symbol: str, timeframe: str) -> Dict[str, Any] | None:
        key = self._state_key(name, symbol, timeframe)
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    async def invalidate_indicators(self, symbol: str, timeframe: str) -> None:
        pattern = f"*:{symbol}:{timeframe}*"
        async for key in self.redis.scan_iter(match=pattern):
            await self.redis.delete(key)
