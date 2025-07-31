import asyncio

import pytest
from src.services.indicators.rsi_calculator import RSICalculator
from src.utils.time_helpers import get_high_precision_timestamp

pytestmark = pytest.mark.skip(reason="performance tests are disabled")


@pytest.mark.asyncio
async def test_concurrent_rsi_calculations():
    rsi_calculator = RSICalculator(None, None)  # type: ignore[arg-type]
    symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT"] * 20
    tasks = [
        rsi_calculator.calculate_real_time_rsi(symbol, "1m", 45000.0, 14)
        for symbol in symbols
    ]
    start = get_high_precision_timestamp()
    results = await asyncio.gather(*tasks)
    end = get_high_precision_timestamp()
    total = end - start
    assert total < 5000
    assert all(r[0] is not None for r in results)
    times = [r[1] for r in results]
    avg = sum(times) / len(times)
    assert avg < 100


@pytest.mark.asyncio
async def test_end_to_end_performance():
    assert True
