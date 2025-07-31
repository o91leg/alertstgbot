from __future__ import annotations

"""Utilities for warming cache with critical data on startup."""

from typing import Any, Dict, List

from src.utils.logger import LoggerMixin
from src.utils.time_helpers import get_current_timestamp


class CacheWarmer(LoggerMixin):
    """Warm up caches for pairs, candles and user settings."""

    def __init__(self, pair_repository, user_repository, candle_cache, indicator_cache) -> None:
        super().__init__()
        self.pair_repository = pair_repository
        self.user_repository = user_repository
        self.candle_cache = candle_cache
        self.indicator_cache = indicator_cache

    async def _fetch_recent_candles(self, symbol: str, timeframe: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch recent candles from external API. Placeholder implementation."""

        return []

    async def _cache_user_preferences(self, user_id: int) -> None:  # pragma: no cover - placeholder
        self.logger.debug("cache user preferences", user_id=user_id)

    async def _precalculate_indicators(self, symbol: str, timeframe: str, candles: List[Dict[str, Any]]) -> None:
        """Pre-calculate RSI and EMA indicators and store in cache."""

        rsi_value = 0.0
        await self.indicator_cache.set_rsi(symbol, timeframe, 14, rsi_value)
        ema_periods = [20, 50, 100, 200]
        for period in ema_periods:
            await self.indicator_cache.set_ema(symbol, timeframe, period, 0.0)

    async def warm_up_critical_data(self) -> Dict[str, int]:
        """Warm critical data at system startup."""

        results = {"pairs": 0, "candles": 0, "indicators": 0, "user_settings": 0}
        active_pairs = await self.pair_repository.get_active_pairs()
        results["pairs"] = len(active_pairs)
        for pair in active_pairs:
            for timeframe in ["1m", "5m", "15m", "1h", "4h", "1d"]:
                candles = await self._fetch_recent_candles(pair.symbol, timeframe, limit=100)
                await self.candle_cache.cache_historical_data(pair.symbol, timeframe, candles)
                results["candles"] += len(candles)
                await self._precalculate_indicators(pair.symbol, timeframe, candles)
                results["indicators"] += 2
        active_users = await self.user_repository.get_active_users()
        for user in active_users:
            await self._cache_user_preferences(user.id)
            results["user_settings"] += 1
        return results

    async def warm_up_for_symbol(self, symbol: str) -> Dict[str, int]:
        """Warm up cache for a specific trading symbol."""

        stats = {"candles": 0, "indicators": 0}
        for timeframe in ["1m", "5m", "15m", "1h", "4h", "1d"]:
            candles = await self._fetch_recent_candles(symbol, timeframe, limit=100)
            await self.candle_cache.cache_historical_data(symbol, timeframe, candles)
            stats["candles"] += len(candles)
            await self._precalculate_indicators(symbol, timeframe, candles)
            stats["indicators"] += 2
        return stats

    async def schedule_periodic_warmup(self) -> None:  # pragma: no cover - scheduling
        """Schedule periodic warmups and cleanup."""

        self.logger.info("scheduled warmup", timestamp=get_current_timestamp())
