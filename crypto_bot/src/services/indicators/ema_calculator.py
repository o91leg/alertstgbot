from __future__ import annotations

import asyncio
from decimal import Decimal
from typing import Any, Dict, List, Tuple
from datetime import datetime, timezone

from services.cache.indicator_cache import IndicatorCache
from services.cache.candle_cache import CandleCache
from utils.logger import LoggerMixin
from utils.math_helpers import calculate_simple_moving_average
from utils.performance_utils import measure_time
from utils.time_helpers import get_high_precision_timestamp, get_time_since_ms


class EMACalculator(LoggerMixin):
    """Exponential Moving Average real-time calculator."""

    def __init__(self, indicator_cache: IndicatorCache, candle_cache: CandleCache) -> None:
        super().__init__()
        self.indicator_cache = indicator_cache
        self.candle_cache = candle_cache
        self.processing_times: List[int] = []

    @measure_time(target_ms=50)
    async def calculate_real_time_ema(
        self, symbol: str, timeframe: str, current_price: float, period: int
    ) -> Tuple[float | None, int]:
        """Return EMA value for ``symbol`` and processing time in ms."""

        start = get_high_precision_timestamp()
        prev = await self._get_cached_ema_value(symbol, timeframe, period)
        if prev is None:
            prev = await self.calculate_ema(symbol, timeframe, period)
            if prev is None:
                return None, int(get_time_since_ms(start))
        k = Decimal(2) / Decimal(period + 1)
        new_ema = (Decimal(current_price) * k) + (Decimal(prev) * (Decimal(1) - k))
        await self._save_ema_value(symbol, timeframe, period, float(new_ema))
        elapsed = int(get_time_since_ms(start))
        self.processing_times.append(elapsed)
        return float(new_ema), elapsed

    async def calculate_multiple_ema_real_time(
        self, symbol: str, timeframe: str, current_price: float, periods: List[int]
    ) -> Dict[int, Tuple[float | None, int]]:
        results: Dict[int, Tuple[float | None, int]] = {}
        for period in periods:
            ema, t = await self.calculate_real_time_ema(symbol, timeframe, current_price, period)
            results[period] = (ema, t)
        return results

    def update_ema_incremental(
        self, previous_ema: float, price: float, period: int
    ) -> float:
        k = Decimal(2) / Decimal(period + 1)
        return float((Decimal(price) * k) + (Decimal(previous_ema) * (Decimal(1) - k)))

    async def _get_cached_ema_value(
        self, symbol: str, timeframe: str, period: int
    ) -> float | None:
        return await self.indicator_cache.get_ema(symbol, timeframe, period)

    async def _save_ema_value(
        self, symbol: str, timeframe: str, period: int, value: float
    ) -> None:
        await self.indicator_cache.set_ema_real_time(symbol, timeframe, period, value)

    async def calculate_ema(
        self, symbol: str, timeframe: str, period: int
    ) -> float | None:
        prices = await self.candle_cache.get_recent_prices(symbol, timeframe, period * 2)
        if len(prices) < period:
            return None
        sma = calculate_simple_moving_average(prices[:period], period)
        if sma is None:
            return None
        ema = Decimal(sma)
        k = Decimal(2) / Decimal(period + 1)
        for price in prices[period:]:
            ema = (Decimal(price) * k) + (ema * (Decimal(1) - k))
        return float(ema)

    def detect_ema_crossover(
        self,
        ema_short: float,
        ema_long: float,
        prev_short: float,
        prev_long: float,
    ) -> str | None:
        if ema_short > ema_long and prev_short <= prev_long:
            return "bullish"
        if ema_short < ema_long and prev_short >= prev_long:
            return "bearish"
        return None

    def get_performance_stats(self) -> Dict[str, Any]:
        if not self.processing_times:
            return {}
        times = sorted(self.processing_times)
        avg = sum(times) / len(times)
        p95 = times[int(len(times) * 0.95) - 1]
        return {"avg_ms": avg, "max_ms": max(times), "p95_ms": p95}
