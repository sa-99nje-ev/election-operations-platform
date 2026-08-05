"""
Candidate management service for registration, filtering, and candidate limit checks.
"""

import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.candidate import Candidate
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.constituency_repository import ConstituencyRepository
from app.utils.enums import CONFIG
from app.utils.exceptions import (
    DuplicateCandidateError,
    ConstituencyNotFoundError,
    MaxCandidatesReachedError,
    CandidateNotFoundError,
    DatabaseError,
    ValidationError
)


class CandidateService:
    """Business service for candidate operations."""

    def __init__(self, session: Session, candidate_repo: CandidateRepository, constituency_repo: ConstituencyRepository):
        self.session = session
        self.candidate_repo = candidate_repo
        self.constituency_repo = constituency_repo

    def register_candidate(
        self,
        national_id: str,
        full_name: str,
        party: str,
        constituency_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None
    ) -> Candidate:
        """Register a new candidate after enforcing national ID uniqueness and candidate limits."""
        if self.candidate_repo.national_id_exists(national_id):
            raise DuplicateCandidateError(
                f"National ID '{national_id}' already registered to a candidate",
                {'national_id': national_id}
            )

        constituency = self.constituency_repo.get_by_id(constituency_id)
        if not constituency:
            raise ConstituencyNotFoundError(
                f"Constituency '{constituency_id}' not found",
                {'constituency_id': str(constituency_id)}
            )

        if self.candidate_repo.check_constituency_candidate_limit(
            constituency_id, CONFIG.MAX_CANDIDATES_PER_CONSTITUENCY
        ):
            raise MaxCandidatesReachedError(
                f"Constituency '{constituency_id}' has reached the candidate limit "
                f"({CONFIG.MAX_CANDIDATES_PER_CONSTITUENCY})",
                {'constituency_id': str(constituency_id), 'limit': CONFIG.MAX_CANDIDATES_PER_CONSTITUENCY}
            )

        try:
            candidate = Candidate(
                national_id=national_id,
                full_name=full_name,
                party=party,
                constituency_id=constituency_id,
                user_id=user_id
            )
            result = self.candidate_repo.create(candidate)
            self.session.commit()
            return result
        except SQLAlchemyError as e:
            self.session.rollback()
            raise DatabaseError("Failed to register candidate", {'error': str(e)})

    def get_candidate_by_id(self, candidate_id: uuid.UUID) -> Optional[Candidate]:
        """Retrieve candidate by ID."""
        return self.candidate_repo.get_by_id(candidate_id)

    def get_all_candidates(self, skip: int = 0, limit: int = 100) -> List[Candidate]:
        """Get all candidates with pagination."""
        return self.candidate_repo.get_all(skip=skip, limit=limit)

    def count_all_candidates(self) -> int:
        """Get total count of all candidates."""
        return self.candidate_repo.count_all()

    def get_candidates_by_constituency(self, constituency_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Candidate]:
        """Get candidates in a specified constituency."""
        return self.candidate_repo.get_by_constituency(constituency_id, skip=skip, limit=limit)

    def count_candidates_by_constituency(self, constituency_id: uuid.UUID) -> int:
        """Get count of candidates in a constituency."""
        return self.candidate_repo.count_by_constituency(constituency_id)

    def get_candidates_by_party(self, party: str, constituency_id: Optional[uuid.UUID] = None) -> List[Candidate]:
        """Get candidates filtered by political party."""
        return self.candidate_repo.get_by_party(party, constituency_id=constituency_id)

    def search_candidates(
        self,
        search_term: str,
        constituency_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Candidate]:
        """Search candidates by name, party, or national ID with pagination."""
        return self.candidate_repo.search_candidates(search_term, constituency_id=constituency_id, skip=skip, limit=limit)

    def count_search_candidates(self, search_term: str, constituency_id: Optional[uuid.UUID] = None) -> int:
        """Get count of search results."""
        return self.candidate_repo.count_search_candidates(search_term, constituency_id=constituency_id)

    def update_candidate(
        self,
        candidate_id: uuid.UUID,
        updates: Dict[str, Any]
    ) -> Candidate:
        """Update candidate details."""
        candidate = self.candidate_repo.get_by_id(candidate_id)
        if not candidate:
            raise CandidateNotFoundError(f"Candidate '{candidate_id}' not found")

        if 'full_name' in updates:
            if not updates['full_name']:
                raise ValidationError("Full name cannot be empty")
            candidate.full_name = updates['full_name']
        
        if 'party' in updates:
            if not updates['party']:
                raise ValidationError("Party cannot be empty")
            candidate.party = updates['party']
        
        if 'constituency_id' in updates:
            constituency = self.constituency_repo.get_by_id(updates['constituency_id'])
            if not constituency:
                raise ConstituencyNotFoundError(f"Constituency '{updates['constituency_id']}' not found")
            candidate.constituency_id = updates['constituency_id']

        try:
            self.candidate_repo.update(candidate)
            self.session.commit()
            return candidate
        except SQLAlchemyError as e:
            self.session.rollback()
            raise DatabaseError("Failed to update candidate", {'error': str(e)})

    def update_party(self, candidate_id: uuid.UUID, party: str) -> Candidate:
        """Update candidate's political party affiliation."""
        return self.update_candidate(candidate_id, {'party': party})

    def deactivate_candidate(self, candidate_id: uuid.UUID) -> bool:
        """Deactivate candidate record."""
        try:
            result = self.candidate_repo.deactivate_candidate(candidate_id)
            self.session.commit()
            return result
        except SQLAlchemyError as e:
            self.session.rollback()
            raise DatabaseError("Failed to deactivate candidate", {'error': str(e)})

    def activate_candidate(self, candidate_id: uuid.UUID) -> bool:
        """Activate candidate record."""
        try:
            result = self.candidate_repo.activate_candidate(candidate_id)
            self.session.commit()
            return result
        except SQLAlchemyError as e:
            self.session.rollback()
            raise DatabaseError("Failed to activate candidate", {'error': str(e)})