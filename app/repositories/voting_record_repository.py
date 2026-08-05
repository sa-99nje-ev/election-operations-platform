"""
Repository for VotingRecord operations using AsyncSession.
"""

from typing import Optional, Sequence
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.voting_record import VotingRecord
from app.repositories.base import BaseRepository


class VotingRecordRepository(BaseRepository[VotingRecord]):
    def __init__(self, session: AsyncSession):
        super().__init__(VotingRecord, session)

    async def voter_has_voted(self, voter_id: UUID) -> bool:
        """Check if a voter has already cast a vote in the database."""
        stmt = select(VotingRecord).where(VotingRecord.voter_id == voter_id)
        result = await self.session.execute(stmt)
        return result.scalars().first() is not None

    async def get_by_request_id(self, request_id: str) -> Optional[VotingRecord]:
        """Find voting record by idempotent request UUID."""
        stmt = select(VotingRecord).where(VotingRecord.request_id == request_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def count_votes_for_candidate(self, candidate_id: UUID) -> int:
        """Calculate total votes accumulated by candidate."""
        stmt = select(func.count()).select_from(VotingRecord).where(
            VotingRecord.candidate_id == candidate_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_candidate_results_by_constituency(self, constituency_id: UUID) -> Sequence[tuple[UUID, int]]:
        """Aggregate vote tallies per candidate within a constituency."""
        from app.models.candidate import Candidate
        
        stmt = (
            select(VotingRecord.candidate_id, func.count(VotingRecord.id))
            .join(Candidate, VotingRecord.candidate_id == Candidate.id)
            .where(Candidate.constituency_id == constituency_id)
            .group_by(VotingRecord.candidate_id)
        )
        result = await self.session.execute(stmt)
        return result.all()