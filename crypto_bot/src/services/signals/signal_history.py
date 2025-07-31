from __future__ import annotations

"""Utilities for working with signal history and metrics."""

from typing import Any, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from data.repositories.signal_repository import SignalRepository
from utils.logger import LoggerMixin


class SignalHistoryManager(LoggerMixin):
    """Persist and analyse signal history."""

    def __init__(self) -> None:  # noqa: D401 - short
        super().__init__()
        self._repo = SignalRepository()

    async def save_signal_with_metrics(
        self,
        session: AsyncSession,
        user_id: int,
        symbol: str,
        timeframe: str,
        signal_type: str,
        processing_time_ms: int,
        delivery_time_ms: int | None = None,
    ) -> None:
        await self._repo.save_signal_with_metrics(
            session,
            user_id,
            symbol,
            timeframe,
            signal_type,
            processing_time_ms=processing_time_ms,
            delivery_time_ms=delivery_time_ms,
        )

    async def get_user_signal_statistics(
        self, session: AsyncSession, user_id: int
    ) -> Dict[str, Any]:
        return await self._repo.get_performance_stats(session)

    async def get_pair_performance_stats(
        self, session: AsyncSession
    ) -> Dict[str, Any]:
        return await self._repo.get_performance_stats(session)

    async def analyze_signal_effectiveness(self) -> Dict[str, Any]:
        return {}
