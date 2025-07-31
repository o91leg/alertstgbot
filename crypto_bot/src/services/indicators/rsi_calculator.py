import asyncio
from typing import Any, Dict, List, Tuple
import math
from datetime import datetime, timezone, timedelta

from src.services.cache.indicator_cache import IndicatorCache
from src.services.cache.candle_cache import CandleCache
from src.utils.logger import LoggerMixin
from src.utils.math_helpers import safe_divide
from src.utils.performance_utils import measure_time
from src.utils.time_helpers import get_high_precision_timestamp, get_time_since_ms
from src.utils.validators import validate_rsi_inputs


class RSICalculator(LoggerMixin):
    """Calculate Relative Strength Index values in real time."""

    def __init__(self, indicator_cache: IndicatorCache, candle_cache: CandleCache) -> None:
        super().__init__()
        self.indicator_cache = indicator_cache
        self.candle_cache = candle_cache
        self.processing_times: List[int] = []

    @measure_time(target_ms=100)
    async def calculate_real_time_rsi(
        self,
        symbol: str,
        timeframe: str,
        current_price: float,
        period: int = 14,
    ) -> Tuple[float | None, int]:
        """Return RSI value for ``symbol`` and processing time in ms."""

        start = get_high_precision_timestamp()
        state = await self._get_cached_rsi_state(symbol, timeframe, period)
        if state is None:
            rsi, state = await self.calculate_rsi(symbol, timeframe, period)
        else:
            rsi, state = self.update_rsi_incremental(state, current_price, period)
        state["previous_price"] = current_price
        state["last_update"] = datetime.now(timezone.utc).isoformat()
        await self._save_rsi_state(symbol, timeframe, period, state)
        elapsed = int(get_time_since_ms(start))
        self.processing_times.append(elapsed)
        return rsi, elapsed

    def update_rsi_incremental(
        self, state: Dict[str, Any], current_price: float, period: int
    ) -> Tuple[float, Dict[str, Any]]:
        """Update RSI values using incremental formula."""

        previous_price = state.get("previous_price", current_price)
        gain = max(0.0, current_price - previous_price)
        loss = max(0.0, previous_price - current_price)
        avg_gain = (state.get("avg_gain", 0.0) * (period - 1) + gain) / period
        avg_loss = (state.get("avg_loss", 0.0) * (period - 1) + loss) / period
        if avg_loss == 0:
            rsi = 100.0
        else:
            rs = safe_divide(avg_gain, avg_loss)
            rsi = 100 - (100 / (1 + rs))
        state.update({"avg_gain": avg_gain, "avg_loss": avg_loss})
        return rsi, state

    async def _get_cached_rsi_state(
        self, symbol: str, timeframe: str, period: int
    ) -> Dict[str, Any] | None:
        """Return cached RSI state if it is not older than an hour."""

        state = await self.indicator_cache.get_calculation_state(
            "rsi", symbol, timeframe, period
        )
        if not state:
            return None
        ts = state.get("last_update")
        if ts:
            try:
                dt = datetime.fromisoformat(ts)
                if datetime.now(timezone.utc) - dt > timedelta(hours=1):
                    return None
            except Exception:  # noqa: BLE001 - defensive
                return None
        return state

    async def _save_rsi_state(
        self, symbol: str, timeframe: str, period: int, state: Dict[str, Any]
    ) -> None:
        await self.indicator_cache.save_calculation_state(
            "rsi", symbol, timeframe, period, state, ttl=3600
        )

    async def calculate_rsi(
        self, symbol: str, timeframe: str, period: int
    ) -> Tuple[float | None, Dict[str, Any]]:
        """Perform full RSI calculation from historical prices."""

        prices = await self.candle_cache.get_recent_prices(
            symbol, timeframe, limit=period + 1
        )
        if not validate_rsi_inputs(prices, period):
            return None, {}
        gains: List[float] = []
        losses: List[float] = []
        for prev, curr in zip(prices, prices[1:]):
            change = curr - prev
            gains.append(max(0.0, change))
            losses.append(max(0.0, -change))
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        if avg_loss == 0:
            rsi = 100.0
        else:
            rs = safe_divide(avg_gain, avg_loss)
            rsi = 100 - (100 / (1 + rs))
        state = {
            "previous_price": prices[-1],
            "avg_gain": avg_gain,
            "avg_loss": avg_loss,
            "period": period,
            "last_update": datetime.now(timezone.utc).isoformat(),
        }
        await self._save_rsi_state(symbol, timeframe, period, state)
        return rsi, state

    def get_performance_stats(self) -> Dict[str, Any]:
        if not self.processing_times:
            return {}
        times = sorted(self.processing_times)
        avg = sum(times) / len(times)
        p95 = times[int(len(times) * 0.95) - 1]
        return {"avg_ms": avg, "max_ms": max(times), "p95_ms": p95}
