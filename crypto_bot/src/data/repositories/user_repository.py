from __future__ import annotations

"""Repository for :class:`User` model."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from .base_repository import BaseRepository
from data.models import User, UserPair, Pair


class UserRepository(BaseRepository[User]):
    def __init__(self) -> None:
        super().__init__(User)

    async def get_by_telegram_id(
        self, session: AsyncSession, telegram_id: int
    ) -> Optional[User]:
        result = await session.execute(
            select(User).where(User.id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def get_active_users(self, session: AsyncSession) -> List[User]:
        result = await session.execute(select(User).where(User.is_active.is_(True)))
        return result.scalars().all()

    async def get_users_with_real_time(self, session: AsyncSession) -> List[User]:
        result = await session.execute(
            select(User).where(User.real_time_enabled.is_(True))
        )
        return result.scalars().all()

    async def get_users_with_pair_and_timeframe(
        self, session: AsyncSession, symbol: str, timeframe: str
    ) -> List[User]:
        stmt = (
            select(User)
            .join(UserPair, User.id == UserPair.user_id)
            .join(Pair, Pair.id == UserPair.pair_id)
            .options(joinedload(User.user_pairs))
            .where(
                Pair.symbol == symbol,
                User.notifications_enabled.is_(True),
                User.is_active.is_(True),
                UserPair.timeframes.contains({timeframe: True}),
            )
        )
        result = await session.execute(stmt)
        return result.scalars().all()
