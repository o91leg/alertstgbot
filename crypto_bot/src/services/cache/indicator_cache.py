from __future__ import annotations

"""Caching of indicator values such as RSI and EMA with real-time helpers."""

from typing import Any, Dict, List, Tuple

import base64
import gzip
import orjson
from redis.asyncio import Redis

from utils.time_helpers import get_current_timestamp, get_high_precision_timestamp


class IndicatorCache:
    """Cache for technical indicators with batching and compression."""

    def __init__(self, redis: Redis, ttl: int = 30, state_ttl: int = 300) -> None:
        self.redis = redis
        self.ttl = ttl
        self.state_ttl = state_ttl

    # ------------------------------------------------------------------
    # key helpers
    def _get_rsi_key(self, symbol: str, timeframe: str, period: int) -> str:
        return f"rsi:{symbol}:{timeframe}:{period}"

    def _get_ema_key(self, symbol: str, timeframe: str, period: int) -> str:
        return f"ema:{symbol}:{timeframe}:{period}"

    def _get_volume_key(self, symbol: str, timeframe: str) -> str:
        return f"vol:{symbol}:{timeframe}"

    @staticmethod
    def _get_real_time_key(base: str) -> str:
        return f"{base}_rt"

    def _state_key(self, name: str, symbol: str, timeframe: str) -> str:
        return f"state:{name}:{symbol}:{timeframe}"

    def _calc_state_key(self, indicator: str, symbol: str, timeframe: str, period: int) -> str:
        return f"state:{indicator}:{symbol}:{timeframe}:{period}"

    # ------------------------------------------------------------------
    # serialization helpers
    @staticmethod
    def _serialize(data: Dict[str, Any]) -> str:
        raw = orjson.dumps(data)
        if len(raw) > 1024:
            compressed = gzip.compress(raw)
            return "gz:" + base64.b64encode(compressed).decode()
        return raw.decode()

    @staticmethod
    def _deserialize(data: str | None) -> Dict[str, Any] | None:
        if data is None:
            return None
        if data.startswith("gz:"):
            decompressed = gzip.decompress(base64.b64decode(data[3:]))
            return orjson.loads(decompressed)
        return orjson.loads(data)

    # ------------------------------------------------------------------
    # adaptive ttl
    @staticmethod
    def _calculate_adaptive_ttl(symbol: str, volatility: float) -> int:
        base_ttl = 300
        if volatility > 0.05:
            return base_ttl // 2
        if volatility < 0.01:
            return base_ttl * 2
        return base_ttl

    # ------------------------------------------------------------------
    # basic getters/setters
    async def get_rsi(self, symbol: str, timeframe: str, period: int) -> float | None:
        value = await self.redis.get(self._get_rsi_key(symbol, timeframe, period))
        return float(value) if value is not None else None

    async def set_rsi(self, symbol: str, timeframe: str, period: int, value: float) -> None:
        await self.redis.set(self._get_rsi_key(symbol, timeframe, period), value, ex=self.ttl)

    async def get_ema(self, symbol: str, timeframe: str, period: int) -> float | None:
        value = await self.redis.get(self._get_ema_key(symbol, timeframe, period))
        return float(value) if value is not None else None

    async def set_ema(self, symbol: str, timeframe: str, period: int, value: float) -> None:
        await self.redis.set(self._get_ema_key(symbol, timeframe, period), value, ex=self.ttl)

    # ------------------------------------------------------------------
    # real-time helpers
    async def set_rsi_real_time(
        self,
        symbol: str,
        timeframe: str,
        period: int,
        value: float,
        ttl: int = 30,
    ) -> bool:
        """Store real-time RSI value with previous state."""

        key = self._get_real_time_key(self._get_rsi_key(symbol, timeframe, period))
        data = {
            "value": value,
            "timestamp": get_high_precision_timestamp(),
            "period": period,
        }
        pipeline = self.redis.pipeline()
        pipeline.setex(key, ttl, self._serialize(data))
        prev_key = f"{key}:prev"
        current_value = await self.redis.get(key)
        if current_value:
            pipeline.setex(prev_key, ttl * 2, current_value)
        await pipeline.execute()
        return True

    async def get_rsi_with_previous(
        self, symbol: str, timeframe: str, period: int
    ) -> Tuple[float | None, float | None, int | None]:
        """Return current RSI, previous RSI and time difference."""

        key = self._get_real_time_key(self._get_rsi_key(symbol, timeframe, period))
        prev_key = f"{key}:prev"
        current_raw, prev_raw = await self.redis.mget([key, prev_key])
        if not current_raw:
            return None, None, None
        current = self._deserialize(current_raw)
        previous = self._deserialize(prev_raw) if prev_raw else None
        current_val = float(current["value"])
        previous_val = float(previous["value"]) if previous else None
        time_diff = (
            current["timestamp"] - previous["timestamp"] if previous else None
        )
        return current_val, previous_val, time_diff

    async def set_multiple_ema_real_time(
        self,
        symbol: str,
        timeframe: str,
        ema_values: Dict[int, Dict[str, float]],
        ttl: int = 30,
    ) -> None:
        """Save EMA values for multiple periods using MSET."""

        mapping: Dict[str, bytes] = {}
        timestamp = get_high_precision_timestamp()
        for period, info in ema_values.items():
            key = self._get_real_time_key(self._get_ema_key(symbol, timeframe, period))
            value = {
                "value": info.get("value"),
                "timestamp": timestamp,
                "slope": info.get("slope"),
            }
            mapping[key] = self._serialize(value)
        pipeline = self.redis.pipeline()
        pipeline.mset(mapping)
        for key in mapping:
            pipeline.expire(key, ttl)
        await pipeline.execute()

    async def get_indicators_batch(
        self,
        symbol: str,
        timeframe: str,
    ) -> Dict[str, Any]:
        """Fetch all indicators for a pair in a single request."""

        rsi_periods = [14, 21]
        ema_periods = [20, 50, 100, 200]
        rsi_keys = [self._get_rsi_key(symbol, timeframe, p) for p in rsi_periods]
        ema_keys = [self._get_ema_key(symbol, timeframe, p) for p in ema_periods]
        volume_key = self._get_volume_key(symbol, timeframe)
        all_keys: List[str] = rsi_keys + ema_keys + [volume_key]
        values = await self.redis.mget(all_keys)
        result: Dict[str, Any] = {
            "rsi": {},
            "ema": {},
            "volume_change": None,
            "last_update": get_current_timestamp(),
        }
        for idx, val in enumerate(values[: len(rsi_keys)]):
            if val is not None:
                result["rsi"][str(rsi_periods[idx])] = float(val)
        offset = len(rsi_keys)
        for jdx, val in enumerate(values[offset : offset + len(ema_keys)]):
            if val is not None:
                result["ema"][str(ema_periods[jdx])] = float(val)
        if values[-1] is not None:
            try:
                result["volume_change"] = float(values[-1])
            except (TypeError, ValueError):
                result["volume_change"] = None
        return result

    # ------------------------------------------------------------------
    async def save_indicator_state(self, name: str, symbol: str, timeframe: str, state: Dict[str, Any]) -> None:
        key = self._state_key(name, symbol, timeframe)
        await self.redis.set(key, self._serialize(state), ex=self.state_ttl)

    async def get_indicator_state(self, name: str, symbol: str, timeframe: str) -> Dict[str, Any] | None:
        key = self._state_key(name, symbol, timeframe)
        data = await self.redis.get(key)
        return self._deserialize(data)

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
        await self.redis.set(key, self._serialize(state), ex=ttl or self.state_ttl)

    async def get_calculation_state(
        self, indicator: str, symbol: str, timeframe: str, period: int
    ) -> Dict[str, Any] | None:
        key = self._calc_state_key(indicator, symbol, timeframe, period)
        data = await self.redis.get(key)
        return self._deserialize(data)

    async def invalidate_indicators(self, symbol: str, timeframe: str) -> None:
        pattern = f"*:{symbol}:{timeframe}*"
        async for key in self.redis.scan_iter(match=pattern):
            await self.redis.delete(key)
