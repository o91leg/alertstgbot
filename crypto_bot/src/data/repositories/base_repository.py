from __future__ import annotations

"""Generic asynchronous repository with CRUD operations."""

from typing import Any, Generic, Iterable, List, Optional, Sequence, Type, TypeVar
from time import perf_counter

from sqlalchemy import update, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.models import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """Base repository providing common CRUD helpers."""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def create(self, session: AsyncSession, obj_in: dict[str, Any]) -> ModelType:
        obj = self.model(**obj_in)
        session.add(obj)
        await session.flush()
        return obj

    async def get_by_id(self, session: AsyncSession, obj_id: Any) -> Optional[ModelType]:
        result = await session.execute(select(self.model).where(self.model.id == obj_id))
        return result.scalar_one_or_none()

    async def get_all(self, session: AsyncSession) -> Sequence[ModelType]:
        result = await session.execute(select(self.model))
        return result.scalars().all()

    async def update(self, session: AsyncSession, obj_id: Any, obj_in: dict[str, Any]) -> Optional[ModelType]:
        await session.execute(
            update(self.model).where(self.model.id == obj_id).values(**obj_in)
        )
        await session.flush()
        return await self.get_by_id(session, obj_id)

    async def delete(self, session: AsyncSession, obj_id: Any) -> None:
        await session.execute(delete(self.model).where(self.model.id == obj_id))

    async def bulk_create(self, session: AsyncSession, objs_in: Iterable[dict[str, Any]]) -> List[ModelType]:
        objs = [self.model(**data) for data in objs_in]
        session.add_all(objs)
        await session.flush()
        return objs

    async def get_with_performance_tracking(
        self, session: AsyncSession, obj_id: Any
    ) -> tuple[Optional[ModelType], int]:
        """Fetch object by id and return time taken in milliseconds."""

        start = perf_counter()
        obj = await self.get_by_id(session, obj_id)
        elapsed_ms = int((perf_counter() - start) * 1000)
        return obj, elapsed_ms

    async def bulk_update_optimized(
        self, session: AsyncSession, mappings: Iterable[dict[str, Any]]
    ) -> None:
        """Perform optimized bulk update using mappings."""

        await session.bulk_update_mappings(self.model, list(mappings))
