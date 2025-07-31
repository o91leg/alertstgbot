from __future__ import annotations

"""Caching of candle (kline) data in Redis."""

import json
from typing import Any, Dict, List

from redis.asyncio import Redis


class CandleCache:
    """Cache wrapper storing candles in Redis sorted sets."""

    def __init__(self, redis: Redis, ttl: int = 600) -> None:
        self.redis = redis
        self.ttl = ttl

    def _key(self, symbol: str, timeframe: str) -> str:
        return f"candles:{symbol}:{timeframe}"

    async def get_candles(self, symbol: str, timeframe: str, limit: int = 100) -> List[Dict[str, Any]]:
        key = self._key(symbol, timeframe)
        raw = await self.redis.zrange(key, -limit, -1)
        return [json.loads(item) for item in raw]

    async def add_new_candle(self, symbol: str, timeframe: str, candle: Dict[str, Any]) -> None:
        key = self._key(symbol, timeframe)
        score = candle.get("close_time") or candle.get("t") or 0
        await self.redis.zadd(key, {json.dumps(candle): score})
        await self.redis.expire(key, self.ttl)

    async def update_last_candle(self, symbol: str, timeframe: str, candle: Dict[str, Any]) -> None:
        await self.add_new_candle(symbol, timeframe, candle)

    async def cache_historical_data(self, symbol: str, timeframe: str, candles: List[Dict[str, Any]]) -> None:
        for candle in candles:
            await self.add_new_candle(symbol, timeframe, candle)

    async def get_last_price_real_time(self, symbol: str, timeframe: str) -> float | None:
        candles = await self.get_candles(symbol, timeframe, limit=1)
        if not candles:
            return None
        return float(candles[-1].get("close_price") or candles[-1].get("c"))

    async def get_recent_prices(self, symbol: str, timeframe: str, limit: int = 50) -> List[float]:
        candles = await self.get_candles(symbol, timeframe, limit)
        return [float(c.get("close_price") or c.get("c", 0.0)) for c in candles]

    async def clear_cache(self, symbol: str, timeframe: str) -> None:
        await self.redis.delete(self._key(symbol, timeframe))

    async def get_cache_stats(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        key = self._key(symbol, timeframe)
        count = await self.redis.zcard(key)
        return {"count": count}
