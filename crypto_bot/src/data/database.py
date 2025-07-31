from __future__ import annotations

"""Database engine and session setup for the application."""

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

from src.config.database_config import get_database_config

_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


class Base(DeclarativeBase):
    """Base class for all models.

    This class exists here to make type checkers happy when importing from
    database module. The real Base with timestamp columns is defined in
    ``data/models/base_model.py`` and should inherit from this one.
    """


async def init_database() -> None:
    """Initialize database engine and session factory."""

    global _engine, _sessionmaker
    if _engine is not None:
        return

    config = get_database_config()
    connect_args = {}
    if config.ssl_mode:
        connect_args["ssl"] = config.ssl_mode

    _engine = create_async_engine(
        config.database_url,
        echo=False,
        pool_size=config.pool_size,
        max_overflow=config.max_overflow,
        pool_timeout=config.pool_timeout,
        connect_args=connect_args,
    )
    _sessionmaker = async_sessionmaker(bind=_engine, expire_on_commit=False)


async def close_database() -> None:
    """Dispose the engine and close all connections."""

    global _engine, _sessionmaker
    if _sessionmaker is not None:
        _sessionmaker.close_all()  # type: ignore[func-returns-value]
        _sessionmaker = None
    if _engine is not None:
        await _engine.dispose()
        _engine = None


def get_engine() -> AsyncEngine:
    """Get the current database engine."""
    global _engine
    if _engine is None:
        raise RuntimeError("Database is not initialized")
    return _engine


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    if _sessionmaker is None:
        raise RuntimeError("Database is not initialized")
    return _sessionmaker


async def test_connection() -> bool:
    """Test database connectivity by executing a simple query."""

    if _engine is None:
        await init_database()
    assert _engine is not None
    try:
        async with _engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
