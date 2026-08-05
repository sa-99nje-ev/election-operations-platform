"""
Repository for RefreshToken operations using AsyncSession.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.refresh_token import RefreshToken
from app.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, session: AsyncSession):
        super().__init__(RefreshToken, session)

    async def get_valid_token(self, token_hash: str) -> Optional[RefreshToken]:
        """Fetch active token that has not expired or been revoked."""
        stmt = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_revoked.is_(False),
            RefreshToken.expires_at > datetime.utcnow()
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def revoke_user_tokens(self, user_id: UUID) -> int:
        """Revoke all active refresh tokens for a user (e.g., password change or logout)."""
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.is_revoked.is_(False))
            .values(is_revoked=True)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount