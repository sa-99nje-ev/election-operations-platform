"""
Repository for Voter entity operations using AsyncSession.
"""

from typing import Optional, Sequence
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.voter import Voter
from app.repositories.base import BaseRepository


class VoterRepository(BaseRepository[Voter]):
    def __init__(self, session: AsyncSession):
        super().__init__(Voter, session)

    async def get_by_national_id(self, national_id: str) -> Optional[Voter]:
        """Retrieve voter by unique national identifier."""
        stmt = select(Voter).where(Voter.national_id == national_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_constituency(self, constituency_id: UUID) -> Sequence[Voter]:
        """Retrieve voters registered under a specific constituency."""
        stmt = select(Voter).where(Voter.constituency_id == constituency_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_status(self, voter_id: UUID, status: str) -> bool:
        """Update voter operational status (ACTIVE, INACTIVE, VOTED)."""
        voter = await self.get_by_id(voter_id)
        if not voter:
            return False
        voter.status = status
        await self.session.flush()
        return True