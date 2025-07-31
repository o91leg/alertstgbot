from __future__ import annotations

"""Repository for :class:`User` model."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base_repository import BaseRepository
from data.models import User


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
