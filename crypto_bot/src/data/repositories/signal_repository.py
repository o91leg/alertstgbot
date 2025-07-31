from __future__ import annotations

"""Repository for :class:`SignalHistory` model."""

from typing import List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .base_repository import BaseRepository
from data.models import SignalHistory


class SignalRepository(BaseRepository[SignalHistory]):
    def __init__(self) -> None:
        super().__init__(SignalHistory)

    async def get_recent_signals(
        self, session: AsyncSession, limit: int = 100
    ) -> List[SignalHistory]:
        result = await session.execute(
            select(SignalHistory).order_by(SignalHistory.sent_at.desc()).limit(limit)
        )
        return result.scalars().all()

    async def get_performance_stats(self, session: AsyncSession) -> dict[str, float]:
        result = await session.execute(
            select(
                func.avg(SignalHistory.processing_time_ms),
                func.avg(SignalHistory.delivery_time_ms),
            )
        )
        avg_processing, avg_delivery = result.one()
        return {
            "avg_processing_ms": float(avg_processing or 0),
            "avg_delivery_ms": float(avg_delivery or 0),
        }
