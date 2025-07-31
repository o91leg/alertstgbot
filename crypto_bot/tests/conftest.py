# flake8: noqa
import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_engine():
    from src.data.database import Base

    """Create test database engine."""
    test_db_url = "postgresql+asyncpg://test:test@localhost:5432/crypto_bot_test"
    engine = create_async_engine(test_db_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    """Yield database session wrapped in transaction."""
    Session = sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with Session() as session:
        transaction = await session.begin()
        yield session
        await transaction.rollback()


@pytest.fixture
def mock_redis():
    """Return mocked Redis client."""
    redis_mock = AsyncMock()
    redis_mock.get.return_value = None
    redis_mock.set.return_value = True
    redis_mock.zadd.return_value = 1
    redis_mock.zrevrange.return_value = []
    redis_mock.pipeline.return_value = AsyncMock()
    return redis_mock


@pytest.fixture
def mock_binance_api():
    """Return mocked Binance API client."""
    api_mock = AsyncMock()
    api_mock.get_exchange_info.return_value = {
        "symbols": [
            {
                "symbol": "BTCUSDT",
                "baseAsset": "BTC",
                "quoteAsset": "USDT",
                "status": "TRADING",
            }
        ]
    }
    api_mock.get_klines.return_value = [
        [1625097600000, "45000.00", "45100.00", "44900.00", "45050.00", "100.0"]
    ]
    return api_mock
