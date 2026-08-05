"""
Voter management service handling registration, lookups, and eligibility verification.
"""

import uuid
from datetime import date
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.voter import Voter
from app.repositories.voter_repository import VoterRepository
from app.repositories.constituency_repository import ConstituencyRepository
from app.utils.enums import VoterStatus
from app.utils.exceptions import (
    VoterNotFoundError,
    DuplicateVoterError,
    ConstituencyNotFoundError,
    DatabaseError,
    ValidationError,
    InvalidNationalIdError,
    InvalidDateError
)


class VoterService:
    """Business service for voter registration and management."""

    def __init__(self, session: Session, voter_repo: VoterRepository, constituency_repo: ConstituencyRepository):
        self.session = session
        self.voter_repo = voter_repo
        self.constituency_repo = constituency_repo

    def register_voter(
        self,
        national_id: str,
        full_name: str,
        dob: date,
        constituency_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None
    ) -> Voter:
        """Register a new voter after verifying uniqueness and constituency existence."""
        if not national_id or len(national_id) < 4:
            raise InvalidNationalIdError("National ID is required and must be at least 4 characters")

        if self.voter_repo.national_id_exists(national_id):
            raise DuplicateVoterError(
                f"National ID '{national_id}' is already registered",
                {'national_id': national_id}
            )

        constituency = self.constituency_repo.get_by_id(constituency_id)
        if not constituency:
            raise ConstituencyNotFoundError(
                f"Constituency '{constituency_id}' not found",
                {'constituency_id': str(constituency_id)}
            )

        try:
            voter = Voter(
                national_id=national_id,
                full_name=full_name,
                dob=dob,
                constituency_id=constituency_id,
                user_id=user_id,
                status=VoterStatus.ACTIVE.value
            )
            result = self.voter_repo.create(voter)
            self.session.commit()
            return result
        except SQLAlchemyError as e:
            self.session.rollback()
            raise DatabaseError("Failed to register voter", {'error': str(e)})

    def get_voter_by_id(self, voter_id: uuid.UUID) -> Optional[Voter]:
        """Retrieve voter by ID."""
        return self.voter_repo.get_by_id(voter_id)

    def get_voter_by_national_id(self, national_id: str) -> Optional[Voter]:
        """Retrieve voter by government-issued national ID."""
        return self.voter_repo.get_by_national_id(national_id)

    def get_all_voters(self, skip: int = 0, limit: int = 100) -> List[Voter]:
        """Get all voters with pagination."""
        return self.voter_repo.get_all(skip=skip, limit=limit)

    def count_all_voters(self) -> int:
        """Get total count of all voters."""
        return self.voter_repo.count_all()

    def get_voters_by_constituency(self, constituency_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Voter]:
        """Retrieve all voters in a specified constituency."""
        return self.voter_repo.get_by_constituency(constituency_id, skip=skip, limit=limit)

    def count_voters_by_constituency(self, constituency_id: uuid.UUID) -> int:
        """Get count of voters in a constituency."""
        return self.voter_repo.count_by_constituency(constituency_id)

    def search_voters(
        self,
        search_term: str,
        constituency_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Voter]:
        """Search voters by name or national ID with pagination."""
        return self.voter_repo.search_voters(search_term, constituency_id=constituency_id, skip=skip, limit=limit)

    def count_search_voters(self, search_term: str, constituency_id: Optional[uuid.UUID] = None) -> int:
        """Get count of search results."""
        return self.voter_repo.count_search_voters(search_term, constituency_id=constituency_id)

    def update_voter(
        self,
        voter_id: uuid.UUID,
        updates: Dict[str, Any]
    ) -> Voter:
        """Update voter details."""
        voter = self.voter_repo.get_by_id(voter_id)
        if not voter:
            raise VoterNotFoundError(f"Voter '{voter_id}' not found")

        if 'full_name' in updates:
            if not updates['full_name']:
                raise ValidationError("Full name cannot be empty")
            voter.full_name = updates['full_name']
        
        if 'constituency_id' in updates:
            constituency = self.constituency_repo.get_by_id(updates['constituency_id'])
            if not constituency:
                raise ConstituencyNotFoundError(f"Constituency '{updates['constituency_id']}' not found")
            voter.constituency_id = updates['constituency_id']
        
        if 'status' in updates:
            if updates['status'] not in [s.value for s in VoterStatus]:
                raise ValidationError(f"Invalid status: {updates['status']}")
            voter.status = updates['status']

        try:
            self.voter_repo.update(voter)
            self.session.commit()
            return voter
        except SQLAlchemyError as e:
            self.session.rollback()
            raise DatabaseError("Failed to update voter", {'error': str(e)})

    def deactivate_voter(self, voter_id: uuid.UUID) -> bool:
        """Deactivate a voter profile."""
        try:
            result = self.voter_repo.deactivate_voter(voter_id)
            self.session.commit()
            return result
        except SQLAlchemyError as e:
            self.session.rollback()
            raise DatabaseError("Failed to deactivate voter", {'error': str(e)})

    def activate_voter(self, voter_id: uuid.UUID) -> bool:
        """Activate a voter profile."""
        try:
            result = self.voter_repo.activate_voter(voter_id)
            self.session.commit()
            return result
        except SQLAlchemyError as e:
            self.session.rollback()
            raise DatabaseError("Failed to activate voter", {'error': str(e)})