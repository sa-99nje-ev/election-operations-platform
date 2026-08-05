"""
Vote Processing Service - Owns the database transaction boundary.
Worker responsibilities: receive payload, validate, persist, commit.
"""

import uuid
import time
import logging
import traceback
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.models.voting_record import VotingRecord
from app.repositories.voting_record_repository import VotingRecordRepository
from app.repositories.voter_repository import VoterRepository
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.polling_booth_repository import PollingBoothRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.utils.enums import VoterStatus, BoothStatus, AuditOutcome, AuditEventType
from app.utils.exceptions import (
    VoterNotFoundError,
    DuplicateVoteError,
    CandidateNotFoundError,
    CandidateNotInConstituencyError,
    BoothNotFoundError,
    BoothClosedError,
    InvalidConstituencyError,
    DatabaseError
)

logger = logging.getLogger(__name__)


class VoteProcessingService:
    """
    Service responsible for processing votes in the background.
    Owns the transaction boundary and contains ALL validation/persistence logic.
    """
    
    def __init__(self, session: Session):
        self.session = session
        self.voter_repo = VoterRepository(session)
        self.candidate_repo = CandidateRepository(session)
        self.booth_repo = PollingBoothRepository(session)
        self.voting_repo = VotingRecordRepository(session)
        self.audit_repo = AuditLogRepository(session)
    
    def process_vote(
        self,
        request_id: str,
        voter_id_str: str,
        candidate_id_str: str,
        booth_id_str: str,
        ip_address: Optional[str] = None,
        trace_id: Optional[str] = None,
        worker_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a vote with full validation and persistence.
        ALL database writes happen in a single transaction.
        """
        start_time = time.time()
        
        try:
            request_uuid = uuid.UUID(request_id)
            voter_id = uuid.UUID(voter_id_str)
            candidate_id = uuid.UUID(candidate_id_str)
            booth_id = uuid.UUID(booth_id_str)
        except ValueError as e:
            raise ValueError(f"Invalid UUID format: {e}")
        
        # 1. Validate Voter
        voter = self.voter_repo.get_by_id(voter_id)
        if not voter or voter.status != VoterStatus.ACTIVE.value:
            raise VoterNotFoundError(f"Voter '{voter_id}' is not active or not found")
        
        # 2. Check for duplicate vote in database (PostgreSQL UNIQUE constraint is the source of truth)
        if self.voting_repo.voter_has_voted(voter_id):
            raise DuplicateVoteError(f"Voter '{voter_id}' has already voted")
        
        # 3. Validate Candidate
        candidate = self.candidate_repo.get_by_id(candidate_id)
        if not candidate:
            raise CandidateNotFoundError(f"Candidate '{candidate_id}' not found")
        
        # 4. Validate Candidate Constituency
        if voter.constituency_id != candidate.constituency_id:
            raise CandidateNotInConstituencyError(
                f"Candidate '{candidate_id}' is not in voter's constituency"
            )
        
        # 5. Validate Booth
        booth = self.booth_repo.get_by_id(booth_id)
        if not booth:
            raise BoothNotFoundError(f"Booth '{booth_id}' not found")
        
        # 6. Validate Booth is OPEN
        if booth.status != BoothStatus.OPEN.value:
            raise BoothClosedError(f"Polling booth '{booth_id}' is closed")
        
        # 7. Validate Booth Constituency
        if booth.constituency_id != voter.constituency_id:
            raise InvalidConstituencyError(
                f"Booth '{booth_id}' is not in voter's constituency"
            )
        
        # 8. Create Voting Record with request_id for idempotency
        voting_record = VotingRecord(
            id=uuid.uuid4(),
            request_id=request_uuid,
            voter_id=voter_id,
            candidate_id=candidate_id,
            booth_id=booth_id
        )
        
        try:
            self.voting_repo.create(voting_record)
        except IntegrityError as e:
            self.session.rollback()
            # Check if it's a duplicate request_id or duplicate voter_id
            if "request_id" in str(e).lower():
                raise DuplicateVoteError(f"Duplicate request_id: {request_id}")
            elif "voter_id" in str(e).lower():
                raise DuplicateVoteError(f"Voter '{voter_id}' has already voted")
            raise DatabaseError(f"Integrity error: {str(e)}")
        
        # 9. Create Audit Log (within same transaction)
        audit_log = self.audit_repo.create_audit_log(
            event_type=AuditEventType.VOTE_COMPLETED.value,
            actor_id=voter_id,
            target_id=candidate_id,
            outcome=AuditOutcome.SUCCESS.value,
            ip_address=ip_address,
            metadata={
                "request_id": request_id,
                "trace_id": trace_id,
                "worker_id": worker_id,
                "voting_record_id": str(voting_record.id)
            }
        )
        
        # 10. Commit Transaction (everything in one atomic unit)
        self.session.commit()
        
        processing_time = round(time.time() - start_time, 4)
        
        logger.info(
            f"Vote processed successfully",
            extra={
                "request_id": request_id,
                "trace_id": trace_id,
                "voter_id": voter_id_str,
                "candidate_id": candidate_id_str,
                "worker_id": worker_id,
                "voting_record_id": str(voting_record.id),
                "processing_time": processing_time,
                "status": "SUCCESS"
            }
        )
        
        return {
            "status": "SUCCESS",
            "request_id": request_id,
            "trace_id": trace_id,
            "voting_record_id": str(voting_record.id),
            "processing_time": processing_time,
            "worker_id": worker_id
        }
    
    def rollback(self) -> None:
        """Rollback the current transaction."""
        self.session.rollback()
    
    def close(self) -> None:
        """Close the session."""
        self.session.close()