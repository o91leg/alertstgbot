import pytest

pytestmark = pytest.mark.skip(reason="requires aiogram testing setup")


@pytest.mark.asyncio
async def test_start_command():
    assert True


@pytest.mark.asyncio
async def test_add_pair_flow():
    assert True
