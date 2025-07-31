from __future__ import annotations

"""Repository for :class:`Pair` model."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base_repository import BaseRepository
from data.models import Pair


class PairRepository(BaseRepository[Pair]):
    def __init__(self) -> None:
        super().__init__(Pair)

    async def get_by_symbol(self, session: AsyncSession, symbol: str) -> Optional[Pair]:
        result = await session.execute(select(Pair).where(Pair.symbol == symbol))
        return result.scalar_one_or_none()

    async def get_active_pairs(self, session: AsyncSession) -> List[Pair]:
        result = await session.execute(select(Pair).where(Pair.is_active.is_(True)))
        return result.scalars().all()

    async def get_pairs_for_real_time_monitoring(
        self, session: AsyncSession
    ) -> List[Pair]:
        result = await session.execute(
            select(Pair).where(Pair.real_time_monitoring.is_(True))
        )
        return result.scalars().all()
