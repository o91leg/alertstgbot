from __future__ import annotations

"""Middleware that injects database session into handlers."""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from data.database import get_engine
from utils.logger import LoggerMixin
from utils.performance_utils import TimingContext


class DatabaseMiddleware(BaseMiddleware, LoggerMixin):
    """Create a new DB session for each update and measure performance."""

    def __init__(self, sessionmaker: async_sessionmaker | None = None) -> None:
        super().__init__()
        if sessionmaker is None:
            engine = get_engine()
            self.sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
        else:
            self.sessionmaker = sessionmaker

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with self.sessionmaker() as session:  # type: AsyncSession
            data["session"] = session
            try:
                with TimingContext() as tc:
                    result = await handler(event, data)
                if tc.elapsed_ms > 100:
                    self.logger.warning("slow_db_handler", elapsed_ms=tc.elapsed_ms)
                await session.commit()
                return result
            except Exception as exc:  # pragma: no cover - error path
                await session.rollback()
                self.logger.error("db_error", error=str(exc))
                raise


__all__ = ["DatabaseMiddleware"]
