from __future__ import annotations

import asyncio
import random
from typing import Any, Dict, List, Tuple

from services.indicators.rsi_calculator import RSICalculator
from services.indicators.ema_calculator import EMACalculator
from services.cache.indicator_cache import IndicatorCache
from services.cache.candle_cache import CandleCache


def generate_test_price_data(length: int) -> List[float]:
    price = 100.0
    data = []
    for _ in range(length):
        price += random.uniform(-1, 1)
        data.append(round(price, 2))
    return data


async def benchmark_rsi_calculation(calculator: RSICalculator, symbol: str, timeframe: str, period: int = 14) -> Tuple[float | None, int]:
    prices = generate_test_price_data(period + 1)
    candle_cache: CandleCache = calculator.candle_cache
    await candle_cache.cache_historical_data(symbol, timeframe, [{"close_price": p} for p in prices])
    return await calculator.calculate_real_time_rsi(symbol, timeframe, prices[-1], period)


async def benchmark_ema_calculation(calculator: EMACalculator, symbol: str, timeframe: str, period: int) -> Tuple[float | None, int]:
    prices = generate_test_price_data(period * 2)
    candle_cache: CandleCache = calculator.candle_cache
    await candle_cache.cache_historical_data(symbol, timeframe, [{"close_price": p} for p in prices])
    return await calculator.calculate_real_time_ema(symbol, timeframe, prices[-1], period)


async def benchmark_real_time_processing(processor, candle: Dict[str, Any]) -> Dict[str, Any]:
    return await processor.process_websocket_data(candle)
