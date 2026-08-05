"""
Repository for User entity operations using AsyncSession.
"""

from typing import Optional, List, Sequence
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import joinedload

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_username(self, username: str) -> Optional[User]:
        """Retrieve a user by username (case-insensitive)."""
        stmt = select(User).where(User.username.ilike(username))
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_role(self, role: str) -> Sequence[User]:
        """Retrieve all users matching a specific role."""
        stmt = select(User).where(User.role == role)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def search_users(self, search_term: str) -> Sequence[User]:
        """Search users by username partial match."""
        stmt = select(User).where(User.username.ilike(f"%{search_term}%"))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_active_users(self) -> Sequence[User]:
        """Retrieve users without soft deletion timestamp."""
        stmt = select(User).where(User.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def username_exists(self, username: str, exclude_user_id: Optional[UUID] = None) -> bool:
        """Check if username exists in database."""
        stmt = select(User).where(User.username.ilike(username))
        if exclude_user_id:
            stmt = stmt.where(User.id != exclude_user_id)
        result = await self.session.execute(stmt)
        return result.scalars().first() is not None

    async def update_password(self, user_id: UUID, password_hash: str) -> bool:
        """Update password hash for specified user."""
        user = await self.get_by_id(user_id)
        if not user:
            return False
        user.password_hash = password_hash
        await self.session.flush()
        return True

    async def deactivate_user(self, user_id: UUID) -> bool:
        """Soft-delete user by setting deleted_at timestamp."""
        user = await self.get_by_id(user_id)
        if not user:
            return False
        if user.deleted_at is None:
            user.deleted_at = datetime.utcnow()
            await self.session.flush()
        return True