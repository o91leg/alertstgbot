from __future__ import annotations

"""Aggregate different signal generators."""

from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from src.services.signals.rsi_signals import rsi_signal_generator, RSISignalGenerator
from src.services.signals.ema_signals import ema_signal_generator, EMASignalGenerator
from src.utils.logger import LoggerMixin
from src.utils.performance_utils import measure_time
from src.utils.constants import get_real_time_target


class SignalAggregator(LoggerMixin):
    """Coordinate multiple signal generators in real time."""

    def __init__(
        self,
        rsi_generator: RSISignalGenerator = rsi_signal_generator,
        ema_generator: EMASignalGenerator = ema_signal_generator,
    ) -> None:
        super().__init__()
        self.rsi_generator = rsi_generator
        self.ema_generator = ema_generator

    @measure_time(target_ms=200)
    async def process_candle_update_real_time(
        self,
        session: AsyncSession,
        symbol: str,
        timeframe: str,
        candle_data: Dict[str, Any],
    ) -> int:
        """Process indicators and generate notifications."""

        rsi_value = candle_data.get("rsi")
        ema_values = candle_data.get("ema", {})
        price = candle_data.get("price", 0.0)
        processing_time_ms = candle_data.get("processing_time_ms", 0)
        total = 0
        if rsi_value is not None:
            total += await self._process_rsi_signals_real_time(
                session, symbol, timeframe, rsi_value, price, processing_time_ms
            )
        if ema_values:
            await self._process_ema_signals_real_time(
                symbol, timeframe, ema_values, price
            )
        return total

    async def _process_rsi_signals_real_time(
        self,
        session: AsyncSession,
        symbol: str,
        timeframe: str,
        rsi_value: float,
        price: float,
        processing_time_ms: int,
    ) -> int:
        return await self.rsi_generator.process_rsi_update_real_time(
            session, symbol, timeframe, rsi_value, price, processing_time_ms
        )

    async def _process_ema_signals_real_time(
        self,
        symbol: str,
        timeframe: str,
        ema_values: Dict[int, float],
        price: float,
    ) -> None:
        await self.ema_generator.process_ema_update_real_time(
            symbol, timeframe, ema_values, price
        )

    def validate_processing_performance(self, elapsed_ms: int) -> bool:
        target = get_real_time_target("signal_generation")
        return elapsed_ms <= target if target else True


signal_aggregator = SignalAggregator()
