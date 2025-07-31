from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from src.services.indicators.ema_calculator import EMACalculator
from src.utils.performance_utils import TimingContext


class TestEMACalculator:
    @pytest_asyncio.fixture
    async def ema_calculator(self):
        indicator_cache = AsyncMock()
        candle_cache = AsyncMock()
        return EMACalculator(indicator_cache, candle_cache)

    @pytest.mark.asyncio
    async def test_ema_incremental_accuracy(self, ema_calculator):
        prices = [100, 102, 101, 103, 105, 104, 106]
        ema_calculator.candle_cache.get_recent_prices.return_value = prices
        traditional = await ema_calculator.calculate_ema("T", "1m", period=5)
        ema_calculator.candle_cache.get_recent_prices.return_value = prices[:5]
        initial = await ema_calculator.calculate_ema("T", "1m", period=5)
        current = initial
        for price in prices[5:]:
            current = ema_calculator.update_ema_incremental(current, price, 5)
        assert traditional is not None
        assert abs(traditional - current) < 0.01

    @pytest.mark.asyncio
    async def test_multiple_ema_performance(self, ema_calculator):
        ema_calculator._get_cached_ema_value = AsyncMock(return_value=100.0)
        ema_calculator._save_ema_value = AsyncMock()
        ema_calculator.calculate_ema = AsyncMock(return_value=100.0)
        with TimingContext("multi_ema") as timer:
            result = await ema_calculator.calculate_multiple_ema_real_time(
                "BTCUSDT", "1m", 100.0, [20, 50, 100, 200]
            )
        assert timer.elapsed_ms < 50
        assert len(result) == 4
