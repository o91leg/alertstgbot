from __future__ import annotations

import asyncio
from typing import Any, Dict, Tuple

from src.services.indicators.rsi_calculator import RSICalculator
from src.services.indicators.ema_calculator import EMACalculator
from src.services.real_time.performance_monitor import PerformanceMonitor
from src.services.signals.signal_aggregator import signal_aggregator, SignalAggregator
from src.utils.logger import LoggerMixin
from src.utils.performance_utils import TimingContext
from src.utils.constants import EMA_PERIODS


class RealTimeProcessor(LoggerMixin):
    """Coordinate real-time indicator calculations."""

    def __init__(
        self,
        rsi_calculator: RSICalculator,
        ema_calculator: EMACalculator,
        performance_monitor: PerformanceMonitor,
        signal_aggregator: SignalAggregator = signal_aggregator,
    ) -> None:
        super().__init__()
        self.rsi_calculator = rsi_calculator
        self.ema_calculator = ema_calculator
        self.performance_monitor = performance_monitor
        self.signal_aggregator = signal_aggregator
        self.processing_times: list[int] = []
        self.signal_times: list[int] = []

    async def start(self) -> None:
        self.logger.info("real_time_processor_started")

    async def stop(self) -> None:
        self.logger.info("real_time_processor_stopped")

    async def process_websocket_data(
        self, candle: Dict[str, Any], session: Any | None = None
    ) -> Dict[str, Any]:
        """Process incoming candle data and update indicators."""

        symbol = candle["symbol"]
        timeframe = candle["timeframe"]
        price = float(candle.get("close_price"))
        with TimingContext("total_processing", target_ms=1000) as timer:
            rsi_task = asyncio.create_task(
                self._update_rsi_real_time(symbol, timeframe, price)
            )
            ema_task = asyncio.create_task(
                self._update_ema_real_time(symbol, timeframe, price)
            )
            rsi_result, ema_result = await asyncio.gather(rsi_task, ema_task)
            signals = await self._generate_real_time_notifications(
                session, symbol, timeframe, price, rsi_result, ema_result
            )
        self.processing_times.append(int(timer.elapsed_ms))
        return {
            "rsi": rsi_result,
            "ema": ema_result,
            "signals": signals,
            "processing_time_ms": int(timer.elapsed_ms),
        }

    async def _update_rsi_real_time(
        self, symbol: str, timeframe: str, price: float
    ) -> Tuple[float | None, int]:
        return await self.rsi_calculator.calculate_real_time_rsi(symbol, timeframe, price)

    async def _update_ema_real_time(
        self, symbol: str, timeframe: str, price: float
    ) -> Dict[int, Tuple[float | None, int]]:
        return await self.ema_calculator.calculate_multiple_ema_real_time(
            symbol, timeframe, price, EMA_PERIODS
        )

    async def _generate_real_time_notifications(
        self,
        session: Any | None,
        symbol: str,
        timeframe: str,
        price: float,
        rsi_result: Tuple[float | None, int],
        ema_result: Dict[int, Tuple[float | None, int]],
    ) -> int:
        candle_data = {
            "rsi": rsi_result[0],
            "ema": {p: v[0] for p, v in ema_result.items()},
            "price": price,
            "processing_time_ms": rsi_result[1],
        }
        count = await self.signal_aggregator.process_candle_update_real_time(
            session, symbol, timeframe, candle_data
        )
        self.signal_times.append(count)
        return count

    def get_signal_generation_stats(self) -> Dict[str, float]:
        if not self.signal_times:
            return {}
        avg = sum(self.signal_times) / len(self.signal_times)
        return {"avg_signals": avg}

    def validate_total_processing_time(self, elapsed_ms: int) -> bool:
        return elapsed_ms <= 1000

    def get_processing_performance_stats(self) -> Dict[str, Any]:
        if not self.processing_times:
            return {}
        times = sorted(self.processing_times)
        avg = sum(times) / len(times)
        return {"avg_ms": avg, "max_ms": max(times)}
