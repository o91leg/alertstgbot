from __future__ import annotations

"""Database migration helpers."""

from sqlalchemy.ext.asyncio import AsyncEngine

from src.data.models import BaseModel, User, Pair
from src.data.database import init_database, get_sessionmaker


async def create_all_tables(engine: AsyncEngine | None = None) -> None:
    """Create all database tables."""

    if engine is None:
        await init_database()
        engine = get_sessionmaker().bind  # type: ignore[attr-defined]
    assert engine is not None
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)


async def drop_all_tables(engine: AsyncEngine | None = None) -> None:
    if engine is None:
        await init_database()
        engine = get_sessionmaker().bind  # type: ignore[attr-defined]
    assert engine is not None
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)


async def init_sample_data() -> None:
    """Insert minimal sample data for tests."""

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        user_repo = User(id=1, username="test")
        pair_repo = Pair(symbol="BTCUSDT", base_asset="BTC", quote_asset="USDT")
        session.add_all([user_repo, pair_repo])
        await session.commit()
