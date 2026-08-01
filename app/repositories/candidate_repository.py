"""
Candidate repository for database operations on Candidate entities.

This module implements the CandidateRepository class that provides specialized
database operations for Candidate entities.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
import uuid

from app.models.candidate import Candidate
from .base import BaseRepository


class CandidateRepository(BaseRepository[Candidate]):
    """
    Repository for Candidate entity operations.
    
    Provides specialized queries and operations for Candidate entities beyond
    the generic CRUD operations from BaseRepository.
    """
    
    def __init__(self, session: Session):
        """
        Initialize CandidateRepository with Candidate model class.
        
        Args:
            session: SQLAlchemy database session
        """
        super().__init__(Candidate, session)
    
    def get_by_national_id(self, national_id: str) -> Optional[Candidate]:
        """
        Retrieve a candidate by national ID.
        
        Args:
            national_id: National ID to search for
            
        Returns:
            Candidate entity if found, None otherwise
        """
        return self.session.query(Candidate).filter(
            Candidate.national_id == national_id
        ).first()
    
    def get_by_constituency(self, constituency_id: uuid.UUID) -> List[Candidate]:
        """
        Retrieve all candidates in a specific constituency.
        
        Args:
            constituency_id: Constituency ID to filter by
            
        Returns:
            List of candidates in the specified constituency
        """
        return self.session.query(Candidate).filter(
            Candidate.constituency_id == constituency_id
        ).all()
    
    def get_by_party(self, party: str, constituency_id: Optional[uuid.UUID] = None) -> List[Candidate]:
        """
        Retrieve candidates by political party.
        
        Args:
            party: Political party to filter by
            constituency_id: Optional constituency ID to filter by
            
        Returns:
            List of candidates in the specified party
        """
        query = self.session.query(Candidate).filter(
            Candidate.party.ilike(party)
        )
        
        if constituency_id:
            query = query.filter(Candidate.constituency_id == constituency_id)
        
        return query.all()
    
    def get_by_user_id(self, user_id: uuid.UUID) -> Optional[Candidate]:
        """
        Retrieve a candidate by associated user ID.
        
        Args:
            user_id: User ID to search for
            
        Returns:
            Candidate entity if found, None otherwise
        """
        return self.session.query(Candidate).filter(
            Candidate.user_id == user_id
        ).first()
    
    def get_active_candidates(self) -> List[Candidate]:
        """
        Retrieve all active candidates (candidates without deleted_at timestamp).
        
        Returns:
            List of active candidates
        """
        return self.session.query(Candidate).filter(
            Candidate.deleted_at.is_(None)
        ).all()
    
    def search_candidates(
        self,
        search_term: str,
        constituency_id: Optional[uuid.UUID] = None
    ) -> List[Candidate]:
        """
        Search candidates by name, party, or national ID (partial match, case-insensitive).
        
        Args:
            search_term: Search term to match against names, parties, or national IDs
            constituency_id: Optional constituency ID to filter by
            
        Returns:
            List of candidates matching the search criteria
        """
        query = self.session.query(Candidate).filter(
            or_(
                Candidate.full_name.ilike(f'%{search_term}%'),
                Candidate.party.ilike(f'%{search_term}%'),
                Candidate.national_id.ilike(f'%{search_term}%')
            )
        )
        
        if constituency_id:
            query = query.filter(Candidate.constituency_id == constituency_id)
        
        return query.all()
    
    def national_id_exists(
        self,
        national_id: str,
        exclude_candidate_id: Optional[uuid.UUID] = None
    ) -> bool:
        """
        Check if a national ID already exists for a candidate.
        
        Args:
            national_id: National ID to check
            exclude_candidate_id: Optional candidate ID to exclude from check
            
        Returns:
            True if national ID exists, False otherwise
        """
        query = self.session.query(Candidate).filter(
            Candidate.national_id == national_id
        )
        
        if exclude_candidate_id:
            query = query.filter(Candidate.id != exclude_candidate_id)
        
        return query.first() is not None
    
    def get_candidate_count_by_constituency(self, constituency_id: uuid.UUID) -> int:
        """
        Get the count of candidates in a specific constituency.
        
        Args:
            constituency_id: Constituency ID to count candidates for
            
        Returns:
            Number of candidates in the constituency
        """
        return self.session.query(Candidate).filter(
            Candidate.constituency_id == constituency_id,
            Candidate.deleted_at.is_(None)
        ).count()
    
    def get_candidate_with_user(self, candidate_id: uuid.UUID) -> Optional[Candidate]:
        """
        Retrieve a candidate with their associated user eagerly loaded.
        
        Args:
            candidate_id: Candidate ID to retrieve
            
        Returns:
            Candidate entity with user if found, None otherwise
        """
        from sqlalchemy.orm import joinedload
        
        return self.session.query(Candidate).options(
            joinedload(Candidate.user)
        ).filter(Candidate.id == candidate_id).first()
    
    def get_candidate_with_constituency(self, candidate_id: uuid.UUID) -> Optional[Candidate]:
        """
        Retrieve a candidate with their constituency eagerly loaded.
        
        Args:
            candidate_id: Candidate ID to retrieve
            
        Returns:
            Candidate entity with constituency if found, None otherwise
        """
        from sqlalchemy.orm import joinedload
        
        return self.session.query(Candidate).options(
            joinedload(Candidate.constituency)
        ).filter(Candidate.id == candidate_id).first()
    
    def get_candidates_by_constituency_with_votes(self, constituency_id: uuid.UUID) -> List[Candidate]:
        """
        Retrieve candidates in a constituency with their vote counts.
        
        Note: This is a simplified implementation. In a real application,
        you would join with voting records to get actual vote counts.
        
        Args:
            constituency_id: Constituency ID to filter by
            
        Returns:
            List of candidates in the constituency
        """
        return self.session.query(Candidate).filter(
            Candidate.constituency_id == constituency_id,
            Candidate.deleted_at.is_(None)
        ).all()
    
    def update_party(self, candidate_id: uuid.UUID, party: str) -> bool:
        """
        Update a candidate's political party.
        
        Args:
            candidate_id: Candidate ID to update
            party: New political party
            
        Returns:
            True if party was updated, False if candidate not found
        """
        candidate = self.get_by_id(candidate_id)
        if candidate is None:
            return False
        
        candidate.party = party
        self.session.flush()
        return True
    
    def deactivate_candidate(self, candidate_id: uuid.UUID) -> bool:
        """
        Deactivate a candidate by setting deleted_at timestamp.
        
        Args:
            candidate_id: Candidate ID to deactivate
            
        Returns:
            True if candidate was deactivated, False if candidate not found
        """
        candidate = self.get_by_id(candidate_id)
        if candidate is None:
            return False
        
        # Check if candidate is already deactivated
        if candidate.deleted_at is not None:
            return True
        
        # Import here to avoid circular import
        from datetime import datetime
        candidate.deleted_at = datetime.utcnow()
        self.session.flush()
        return True
    
    def activate_candidate(self, candidate_id: uuid.UUID) -> bool:
        """
        Activate a previously deactivated candidate by clearing deleted_at.
        
        Args:
            candidate_id: Candidate ID to activate
            
        Returns:
            True if candidate was activated, False if candidate not found
        """
        candidate = self.get_by_id(candidate_id)
        if candidate is None:
            return False
        
        # Check if candidate is already active
        if candidate.deleted_at is None:
            return True
        
        candidate.deleted_at = None
        self.session.flush()
        return True
    
    def check_constituency_candidate_limit(self, constituency_id: uuid.UUID, max_candidates: int = 20) -> bool:
        """
        Check if a constituency has reached its candidate limit.
        
        Args:
            constituency_id: Constituency ID to check
            max_candidates: Maximum number of candidates allowed per constituency
            
        Returns:
            True if constituency has reached candidate limit, False otherwise
        """
        candidate_count = self.get_candidate_count_by_constituency(constituency_id)
        return candidate_count >= max_candidates