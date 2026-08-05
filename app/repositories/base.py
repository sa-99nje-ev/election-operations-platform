"""
Generic Base Repository using AsyncSession and SQLAlchemy 2.0 select() queries.
"""

from typing import Generic, TypeVar, Type, Optional, List, Any, Sequence
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Generic async repository providing standard CRUD methods for SQLAlchemy models."""

    def __init__(self, model: Type[T], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, entity_id: UUID) -> Optional[T]:
        """Fetch entity by primary key UUID."""
        return await self.session.get(self.model, entity_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[T]:
        """Retrieve paginated list of entities."""
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, entity: T) -> T:
        """Add new entity to session without committing transaction."""
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def update(self, entity_id: UUID, **kwargs: Any) -> Optional[T]:
        """Update entity attributes by ID."""
        entity = await self.get_by_id(entity_id)
        if not entity:
            return None
        for key, value in kwargs.items():
            if hasattr(entity, key) and value is not None:
                setattr(entity, key, value)
        await self.session.flush()
        return entity

    async def delete(self, entity_id: UUID) -> bool:
        """Delete entity by ID."""
        entity = await self.get_by_id(entity_id)
        if not entity:
            return False
        await self.session.delete(entity)
        await self.session.flush()
        return True

    async def count(self) -> int:
        """Count total records for model."""
        stmt = select(func.count()).select_from(self.model)
        result = await self.session.execute(stmt)
        return result.scalar_one()