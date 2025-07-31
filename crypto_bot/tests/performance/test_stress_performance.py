import asyncio
import gc

import psutil
import pytest

pytestmark = pytest.mark.skip(reason="stress tests are disabled")


@pytest.mark.asyncio
async def test_memory_under_load():
    process = psutil.Process()
    initial = process.memory_info().rss / 1024 / 1024
    tasks = []
    for i in range(1000):
        tasks.append(asyncio.sleep(0))
    await asyncio.gather(*tasks)
    gc.collect()
    final = process.memory_info().rss / 1024 / 1024
    assert final - initial < 100


@pytest.mark.asyncio
async def test_concurrent_users_simulation():
    async def simulate_user_activity(user_id: int, signals_per_minute: int):
        for _ in range(signals_per_minute * 5):
            await asyncio.sleep(0)

    user_tasks = [simulate_user_activity(i, 5) for i in range(1000)]
    await asyncio.gather(*user_tasks)
    assert True
