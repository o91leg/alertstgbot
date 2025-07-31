from __future__ import annotations

"""Repository for user-pair relationships."""

from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base_repository import BaseRepository
from data.models import UserPair, Pair


class UserPairRepository(BaseRepository[UserPair]):
    """Repository providing queries related to :class:`UserPair`."""

    def __init__(self) -> None:
        super().__init__(UserPair)

    async def get_active_symbols(self, session: AsyncSession) -> List[str]:
        """Return symbols of pairs with real-time monitoring enabled."""

        result = await session.execute(
            select(Pair.symbol)
            .join(UserPair, UserPair.pair_id == Pair.id)
            .where(UserPair.real_time_active.is_(True))
        )
        return result.scalars().all()
