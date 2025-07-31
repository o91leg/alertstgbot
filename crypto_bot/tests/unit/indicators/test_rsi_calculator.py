from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from src.services.indicators.rsi_calculator import RSICalculator
from src.utils.performance_utils import TimingContext
from tests.fixtures.test_data import get_expected_rsi_result, get_test_rsi_prices


class TestRSICalculator:
    @pytest_asyncio.fixture
    async def rsi_calculator(self):
        indicator_cache = AsyncMock()
        candle_cache = AsyncMock()
        return RSICalculator(indicator_cache, candle_cache)

    @pytest.mark.asyncio
    async def test_rsi_calculation_accuracy(self, rsi_calculator):
        """Ensure RSI calculation matches known result."""
        prices = get_test_rsi_prices()
        rsi_calculator.candle_cache.get_recent_prices.return_value = prices
        result, _state = await rsi_calculator.calculate_rsi("BTCUSDT", "1m", period=14)
        expected = get_expected_rsi_result()
        assert result is not None
        assert abs(result - expected) < 0.1

    @pytest.mark.asyncio
    async def test_incremental_rsi_performance(self, rsi_calculator):
        """RSI real-time calculation should be fast."""
        state = {
            "previous_price": 45000.0,
            "avg_gain": 150.5,
            "avg_loss": 120.3,
            "period": 14,
        }
        rsi_calculator.indicator_cache.get_calculation_state.return_value = state
        rsi_calculator._save_rsi_state = AsyncMock()
        with TimingContext("incremental_rsi") as timer:
            result, processing_time = await rsi_calculator.calculate_real_time_rsi(
                "BTCUSDT", "1m", 45100.0, 14
            )
        assert timer.elapsed_ms < 100
        assert processing_time < 100
        assert result is not None and 0 <= result <= 100

    @pytest.mark.asyncio
    async def test_rsi_edge_cases(self, rsi_calculator):
        """Handle division by zero and insufficient data."""
        state = {"previous_price": 100.0, "avg_gain": 1.0, "avg_loss": 0.0}
        rsi, _ = rsi_calculator.update_rsi_incremental(state, 101.0, 14)
        assert rsi == 100.0
        rsi_calculator.candle_cache.get_recent_prices.return_value = [1, 2]
        result, state = await rsi_calculator.calculate_rsi("BTCUSDT", "1m", 14)
        assert result is None and state == {}
        state = {"previous_price": 1e6, "avg_gain": 5.0, "avg_loss": 5.0}
        rsi, _ = rsi_calculator.update_rsi_incremental(state, 1e12, 14)
        assert 0 <= rsi <= 100
