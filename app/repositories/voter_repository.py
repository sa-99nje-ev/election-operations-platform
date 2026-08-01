"""
Voter repository for database operations on Voter entities.

This module implements the VoterRepository class that provides specialized
database operations for Voter entities.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
import uuid

from app.models.voter import Voter
from .base import BaseRepository


class VoterRepository(BaseRepository[Voter]):
    """
    Repository for Voter entity operations.
    
    Provides specialized queries and operations for Voter entities beyond
    the generic CRUD operations from BaseRepository.
    """
    
    def __init__(self, session: Session):
        """
        Initialize VoterRepository with Voter model class.
        
        Args:
            session: SQLAlchemy database session
        """
        super().__init__(Voter, session)
    
    def get_by_national_id(self, national_id: str) -> Optional[Voter]:
        """
        Retrieve a voter by national ID.
        
        Args:
            national_id: National ID to search for
            
        Returns:
            Voter entity if found, None otherwise
        """
        return self.session.query(Voter).filter(
            Voter.national_id == national_id
        ).first()
    
    def get_by_constituency(self, constituency_id: uuid.UUID) -> List[Voter]:
        """
        Retrieve all voters in a specific constituency.
        
        Args:
            constituency_id: Constituency ID to filter by
            
        Returns:
            List of voters in the specified constituency
        """
        return self.session.query(Voter).filter(
            Voter.constituency_id == constituency_id
        ).all()
    
    def get_by_polling_booth(self, polling_booth_id: uuid.UUID) -> List[Voter]:
        """
        Retrieve all voters assigned to a specific polling booth.
        
        Args:
            polling_booth_id: Polling booth ID to filter by
            
        Returns:
            List of voters assigned to the specified polling booth
        """
        return self.session.query(Voter).filter(
            Voter.polling_booth_id == polling_booth_id
        ).all()
    
    def get_by_user_id(self, user_id: uuid.UUID) -> Optional[Voter]:
        """
        Retrieve a voter by associated user ID.
        
        Args:
            user_id: User ID to search for
            
        Returns:
            Voter entity if found, None otherwise
        """
        return self.session.query(Voter).filter(
            Voter.user_id == user_id
        ).first()
    
    def get_active_voters(self) -> List[Voter]:
        """
        Retrieve all active voters (voters without deleted_at timestamp).
        
        Returns:
            List of active voters
        """
        return self.session.query(Voter).filter(
            Voter.deleted_at.is_(None)
        ).all()
    
    def search_voters(
        self,
        search_term: str,
        constituency_id: Optional[uuid.UUID] = None
    ) -> List[Voter]:
        """
        Search voters by name or national ID (partial match, case-insensitive).
        
        Args:
            search_term: Search term to match against names or national IDs
            constituency_id: Optional constituency ID to filter by
            
        Returns:
            List of voters matching the search criteria
        """
        query = self.session.query(Voter).filter(
            or_(
                Voter.full_name.ilike(f'%{search_term}%'),
                Voter.national_id.ilike(f'%{search_term}%')
            )
        )
        
        if constituency_id:
            query = query.filter(Voter.constituency_id == constituency_id)
        
        return query.all()
    
    def national_id_exists(
        self,
        national_id: str,
        exclude_voter_id: Optional[uuid.UUID] = None
    ) -> bool:
        """
        Check if a national ID already exists.
        
        Args:
            national_id: National ID to check
            exclude_voter_id: Optional voter ID to exclude from check
            
        Returns:
            True if national ID exists, False otherwise
        """
        query = self.session.query(Voter).filter(
            Voter.national_id == national_id
        )
        
        if exclude_voter_id:
            query = query.filter(Voter.id != exclude_voter_id)
        
        return query.first() is not None
    
    def get_voters_by_age_range(
        self,
        min_age: Optional[int] = None,
        max_age: Optional[int] = None,
        constituency_id: Optional[uuid.UUID] = None
    ) -> List[Voter]:
        """
        Retrieve voters within a specific age range.
        
        Args:
            min_age: Minimum age (inclusive)
            max_age: Maximum age (inclusive)
            constituency_id: Optional constituency ID to filter by
            
        Returns:
            List of voters within the specified age range
        """
        from datetime import date
        from sqlalchemy import extract
        
        query = self.session.query(Voter)
        
        if min_age is not None:
            max_birth_date = date.today().replace(year=date.today().year - min_age)
            query = query.filter(Voter.date_of_birth <= max_birth_date)
        
        if max_age is not None:
            min_birth_date = date.today().replace(year=date.today().year - max_age - 1)
            query = query.filter(Voter.date_of_birth >= min_birth_date)
        
        if constituency_id:
            query = query.filter(Voter.constituency_id == constituency_id)
        
        return query.all()
    
    def get_voter_count_by_constituency(self, constituency_id: uuid.UUID) -> int:
        """
        Get the count of voters in a specific constituency.
        
        Args:
            constituency_id: Constituency ID to count voters for
            
        Returns:
            Number of voters in the constituency
        """
        return self.session.query(Voter).filter(
            Voter.constituency_id == constituency_id,
            Voter.deleted_at.is_(None)
        ).count()
    
    def get_voter_with_user(self, voter_id: uuid.UUID) -> Optional[Voter]:
        """
        Retrieve a voter with their associated user eagerly loaded.
        
        Args:
            voter_id: Voter ID to retrieve
            
        Returns:
            Voter entity with user if found, None otherwise
        """
        from sqlalchemy.orm import joinedload
        
        return self.session.query(Voter).options(
            joinedload(Voter.user)
        ).filter(Voter.id == voter_id).first()
    
    def get_voter_with_constituency(self, voter_id: uuid.UUID) -> Optional[Voter]:
        """
        Retrieve a voter with their constituency eagerly loaded.
        
        Args:
            voter_id: Voter ID to retrieve
            
        Returns:
            Voter entity with constituency if found, None otherwise
        """
        from sqlalchemy.orm import joinedload
        
        return self.session.query(Voter).options(
            joinedload(Voter.constituency)
        ).filter(Voter.id == voter_id).first()
    
    def update_polling_booth(
        self,
        voter_id: uuid.UUID,
        polling_booth_id: uuid.UUID
    ) -> bool:
        """
        Update a voter's assigned polling booth.
        
        Args:
            voter_id: Voter ID to update
            polling_booth_id: New polling booth ID
            
        Returns:
            True if polling booth was updated, False if voter not found
        """
        voter = self.get_by_id(voter_id)
        if voter is None:
            return False
        
        voter.polling_booth_id = polling_booth_id
        self.session.flush()
        return True
    
    def deactivate_voter(self, voter_id: uuid.UUID) -> bool:
        """
        Deactivate a voter by setting deleted_at timestamp.
        
        Args:
            voter_id: Voter ID to deactivate
            
        Returns:
            True if voter was deactivated, False if voter not found
        """
        voter = self.get_by_id(voter_id)
        if voter is None:
            return False
        
        # Check if voter is already deactivated
        if voter.deleted_at is not None:
            return True
        
        # Import here to avoid circular import
        from datetime import datetime
        voter.deleted_at = datetime.utcnow()
        self.session.flush()
        return True
    
    def activate_voter(self, voter_id: uuid.UUID) -> bool:
        """
        Activate a previously deactivated voter by clearing deleted_at.
        
        Args:
            voter_id: Voter ID to activate
            
        Returns:
            True if voter was activated, False if voter not found
        """
        voter = self.get_by_id(voter_id)
        if voter is None:
            return False
        
        # Check if voter is already active
        if voter.deleted_at is None:
            return True
        
        voter.deleted_at = None
        self.session.flush()
        return True