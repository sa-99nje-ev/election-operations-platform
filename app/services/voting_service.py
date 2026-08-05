"""
Voting Service - Validates business rules and enqueues votes into ARQ.
NO database commits - only validation and queue submission.
Audit and persistence happen in the worker transaction.
"""

import uuid
import time
import logging
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from arq import create_pool
from arq.connections import RedisSettings

from app.repositories.voting_record_repository import VotingRecordRepository
from app.repositories.voter_repository import VoterRepository
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.polling_booth_repository import PollingBoothRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.config.settings import settings
from app.utils.enums import VoterStatus, BoothStatus
from app.utils.exceptions import (
    VoterNotFoundError,
    DuplicateVoteError,
    CandidateNotFoundError,
    CandidateNotInConstituencyError,
    BoothNotFoundError,
    BoothClosedError,
    InvalidConstituencyError,
)

logger = logging.getLogger(__name__)


class VotingService:
    """
    Business service handling vote eligibility checks and delegating queueing to ARQ.
    Does NOT commit any database transactions - all persistence happens in the worker.
    """

    def __init__(
        self,
        session: AsyncSession,
        voting_record_repo: VotingRecordRepository,
        voter_repo: VoterRepository,
        candidate_repo: CandidateRepository,
        booth_repo: PollingBoothRepository,
        audit_log_repo: AuditLogRepository,
    ):
        self.session = session
        self.voting_record_repo = voting_record_repo
        self.voter_repo = voter_repo
        self.candidate_repo = candidate_repo
        self.booth_repo = booth_repo
        self.audit_log_repo = audit_log_repo

    async def validate_and_enqueue_vote(
        self,
        voter_id: uuid.UUID,
        candidate_id: uuid.UUID,
        booth_id: uuid.UUID,
        ip_address: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate voter, candidate, booth eligibility and enqueue vote to ARQ.
        NO database commits - only reads and validation.
        """
        # 1. Validate Voter (async read-only)
        voter = await self.voter_repo.get_by_id(voter_id)
        if not voter or voter.status != VoterStatus.ACTIVE.value:
            raise VoterNotFoundError(f"Voter '{voter_id}' is not active or registered")

        # 2. Check for duplicate vote in database (async read-only)
        if await self.voting_record_repo.voter_has_voted(voter_id):
            raise DuplicateVoteError(f"Voter '{voter_id}' has already voted")

        # 3. Validate Candidate (async read-only)
        candidate = await self.candidate_repo.get_by_id(candidate_id)
        if not candidate:
            raise CandidateNotFoundError(f"Candidate '{candidate_id}' not found")

        # 4. Validate Candidate Constituency (read-only)
        if voter.constituency_id != candidate.constituency_id:
            raise CandidateNotInConstituencyError("Candidate is not in voter's constituency")

        # 5. Validate Booth (async read-only)
        booth = await self.booth_repo.get_by_id(booth_id)
        if not booth:
            raise BoothNotFoundError(f"Booth '{booth_id}' not found")

        # 6. Validate Booth is OPEN (read-only)
        if booth.status != BoothStatus.OPEN.value:
            raise BoothClosedError(f"Polling booth '{booth_id}' is closed")

        # 7. Validate Booth Constituency (read-only)
        if booth.constituency_id != voter.constituency_id:
            raise InvalidConstituencyError("Booth is not in voter's constituency")

        # Generate request metadata
        request_id = str(uuid.uuid4())
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        trace_id = trace_id or str(uuid.uuid4())

        # Build payload with full traceability
        payload = {
            "schema_version": 1,
            "api_version": "1.0.0",
            "request_id": request_id,
            "trace_id": trace_id,
            "voter_id": str(voter_id),
            "candidate_id": str(candidate_id),
            "booth_id": str(booth_id),
            "ip_address": ip_address,
            "timestamp": timestamp,
            "constituency_id": str(voter.constituency_id)
        }

        # Enqueue via ARQ Redis Client (no database commit)
        redis = await create_pool(RedisSettings(host=settings.REDIS_HOST, port=settings.REDIS_PORT))
        await redis.enqueue_job("process_vote_task", payload)

        logger.info(
            "Vote validated and enqueued into ARQ",
            extra={
                "request_id": request_id,
                "trace_id": trace_id,
                "voter_id": str(voter_id),
                "candidate_id": str(candidate_id),
                "booth_id": str(booth_id),
                "status": "ENQUEUED"
            }
        )

        return payload

    async def has_voted(self, voter_id: uuid.UUID) -> bool:
        """Check if voter has already voted (async read-only)."""
        return await self.voting_record_repo.voter_has_voted(voter_id)