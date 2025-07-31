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

    def _calc_state_key(
        self, indicator: str, symbol: str, timeframe: str, period: int
    ) -> str:
        return f"state:{indicator}:{symbol}:{timeframe}:{period}"

    async def get_rsi(self, symbol: str, timeframe: str, period: int) -> float | None:
        value = await self.redis.get(self._rsi_key(symbol, timeframe, period))
        return float(value) if value is not None else None

    async def set_rsi(self, symbol: str, timeframe: str, period: int, value: float) -> None:
        await self.redis.set(self._rsi_key(symbol, timeframe, period), value, ex=self.ttl)

    async def set_rsi_real_time(self, symbol: str, timeframe: str, period: int, value: float) -> None:
        await self.redis.set(self._rsi_key(symbol, timeframe, period), value, ex=30)

    async def get_ema(self, symbol: str, timeframe: str, period: int) -> float | None:
        value = await self.redis.get(self._ema_key(symbol, timeframe, period))
        return float(value) if value is not None else None

    async def set_ema(self, symbol: str, timeframe: str, period: int, value: float) -> None:
        await self.redis.set(self._ema_key(symbol, timeframe, period), value, ex=self.ttl)

    async def set_ema_real_time(self, symbol: str, timeframe: str, period: int, value: float) -> None:
        await self.redis.set(self._ema_key(symbol, timeframe, period), value, ex=300)

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

    async def save_calculation_state(
        self,
        indicator: str,
        symbol: str,
        timeframe: str,
        period: int,
        state: Dict[str, Any],
        ttl: int | None = None,
    ) -> None:
        key = self._calc_state_key(indicator, symbol, timeframe, period)
        await self.redis.set(key, json.dumps(state), ex=ttl or self.state_ttl)

    async def get_calculation_state(
        self, indicator: str, symbol: str, timeframe: str, period: int
    ) -> Dict[str, Any] | None:
        key = self._calc_state_key(indicator, symbol, timeframe, period)
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    async def get_indicators_batch(
        self, keys: Dict[str, Tuple[str, str, int]]
    ) -> Dict[str, float | None]:
        pipeline = self.redis.pipeline()
        for name, (symbol, timeframe, period) in keys.items():
            if name == "rsi":
                pipeline.get(self._rsi_key(symbol, timeframe, period))
            else:
                pipeline.get(self._ema_key(symbol, timeframe, period))
        values = await pipeline.execute()
        return {
            key: (float(val) if val is not None else None)
            for key, val in zip(keys.keys(), values)
        }

    async def invalidate_indicators(self, symbol: str, timeframe: str) -> None:
        pattern = f"*:{symbol}:{timeframe}*"
        async for key in self.redis.scan_iter(match=pattern):
            await self.redis.delete(key)
