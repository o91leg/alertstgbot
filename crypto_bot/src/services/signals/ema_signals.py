from __future__ import annotations

"""EMA based signal generator."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from src.utils.logger import LoggerMixin


class EMASignalGenerator(LoggerMixin):
    """Generate signals using exponential moving averages."""

    def __init__(self) -> None:  # noqa: D401 - short
        super().__init__()
        self._previous: Dict[Tuple[str, str, int], float] = {}

    async def process_ema_update_real_time(
        self,
        symbol: str,
        timeframe: str,
        ema_values: Dict[int, float],
        price: float,
    ) -> List[Dict[str, Any]]:
        """Process EMA updates and return detected signals."""

        signals: List[Dict[str, Any]] = []
        signals.extend(self.detect_ema_crossovers(symbol, timeframe, ema_values))
        signals.extend(self.determine_trend_strength(symbol, timeframe, ema_values))
        signals.extend(
            self.check_price_ema_divergence(symbol, timeframe, ema_values, price)
        )
        for period, value in ema_values.items():
            self._previous[(symbol, timeframe, period)] = value
        return signals

    def detect_ema_crossovers(
        self, symbol: str, timeframe: str, ema_values: Dict[int, float]
    ) -> List[Dict[str, Any]]:
        """Detect golden/death cross signals."""

        signals: List[Dict[str, Any]] = []
        pairs = [(20, 50), (50, 200)]
        for short_p, long_p in pairs:
            short = ema_values.get(short_p)
            long = ema_values.get(long_p)
            prev_short = self._previous.get((symbol, timeframe, short_p))
            prev_long = self._previous.get((symbol, timeframe, long_p))
            if (
                short
                and long
                and prev_short is not None
                and prev_long is not None
                and prev_short < prev_long
                and short > long
            ):
                signals.append({"signal_type": "ema_golden_cross", "periods": (short_p, long_p)})
            elif (
                short
                and long
                and prev_short is not None
                and prev_long is not None
                and prev_short > prev_long
                and short < long
            ):
                signals.append({"signal_type": "ema_death_cross", "periods": (short_p, long_p)})
        return signals

    def determine_trend_strength(
        self, symbol: str, timeframe: str, ema_values: Dict[int, float]
    ) -> List[Dict[str, Any]]:
        """Placeholder trend strength analysis."""

        return []

    def check_price_ema_divergence(
        self,
        symbol: str,
        timeframe: str,
        ema_values: Dict[int, float],
        price: float,
    ) -> List[Dict[str, Any]]:
        """Placeholder divergence checks between price and EMA."""

        return []


ema_signal_generator = EMASignalGenerator()
