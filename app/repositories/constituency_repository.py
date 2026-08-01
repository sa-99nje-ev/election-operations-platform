"""
Constituency repository for database operations on Constituency entities.

This module implements the ConstituencyRepository class that provides specialized
database operations for Constituency entities.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
import uuid

from app.models.constituency import Constituency
from .base import BaseRepository


class ConstituencyRepository(BaseRepository[Constituency]):
    """
    Repository for Constituency entity operations.
    
    Provides specialized queries and operations for Constituency entities beyond
    the generic CRUD operations from BaseRepository.
    """
    
    def __init__(self, session: Session):
        """
        Initialize ConstituencyRepository with Constituency model class.
        
        Args:
            session: SQLAlchemy database session
        """
        super().__init__(Constituency, session)
    
    def get_by_code(self, code: str) -> Optional[Constituency]:
        """
        Retrieve a constituency by code.
        
        Args:
            code: Constituency code to search for
            
        Returns:
            Constituency entity if found, None otherwise
        """
        return self.session.query(Constituency).filter(
            Constituency.code == code
        ).first()
    
    def get_by_name(self, name: str) -> Optional[Constituency]:
        """
        Retrieve a constituency by name (case-insensitive).
        
        Args:
            name: Constituency name to search for
            
        Returns:
            Constituency entity if found, None otherwise
        """
        return self.session.query(Constituency).filter(
            Constituency.name.ilike(name)
        ).first()
    
    def get_active_constituencies(self) -> List[Constituency]:
        """
        Retrieve all active constituencies (without deleted_at timestamp).
        
        Returns:
            List of active constituencies
        """
        return self.session.query(Constituency).filter(
            Constituency.deleted_at.is_(None)
        ).all()
    
    def search_constituencies(self, search_term: str) -> List[Constituency]:
        """
        Search constituencies by name or code (partial match, case-insensitive).
        
        Args:
            search_term: Search term to match against names or codes
            
        Returns:
            List of constituencies matching the search term
        """
        return self.session.query(Constituency).filter(
            or_(
                Constituency.name.ilike(f'%{search_term}%'),
                Constituency.code.ilike(f'%{search_term}%')
            ),
            Constituency.deleted_at.is_(None)
        ).all()
    
    def code_exists(
        self,
        code: str,
        exclude_constituency_id: Optional[uuid.UUID] = None
    ) -> bool:
        """
        Check if a constituency code already exists.
        
        Args:
            code: Constituency code to check
            exclude_constituency_id: Optional constituency ID to exclude from check
            
        Returns:
            True if code exists, False otherwise
        """
        query = self.session.query(Constituency).filter(
            Constituency.code == code
        )
        
        if exclude_constituency_id:
            query = query.filter(Constituency.id != exclude_constituency_id)
        
        return query.first() is not None
    
    def name_exists(
        self,
        name: str,
        exclude_constituency_id: Optional[uuid.UUID] = None
    ) -> bool:
        """
        Check if a constituency name already exists (case-insensitive).
        
        Args:
            name: Constituency name to check
            exclude_constituency_id: Optional constituency ID to exclude from check
            
        Returns:
            True if name exists, False otherwise
        """
        query = self.session.query(Constituency).filter(
            Constituency.name.ilike(name)
        )
        
        if exclude_constituency_id:
            query = query.filter(Constituency.id != exclude_constituency_id)
        
        return query.first() is not None
    
    def get_constituency_with_polling_booths(self, constituency_id: uuid.UUID) -> Optional[Constituency]:
        """
        Retrieve a constituency with its polling booths eagerly loaded.
        
        Args:
            constituency_id: Constituency ID to retrieve
            
        Returns:
            Constituency entity with polling booths if found, None otherwise
        """
        from sqlalchemy.orm import joinedload
        
        return self.session.query(Constituency).options(
            joinedload(Constituency.polling_booths)
        ).filter(Constituency.id == constituency_id).first()
    
    def get_constituency_with_candidates(self, constituency_id: uuid.UUID) -> Optional[Constituency]:
        """
        Retrieve a constituency with its candidates eagerly loaded.
        
        Args:
            constituency_id: Constituency ID to retrieve
            
        Returns:
            Constituency entity with candidates if found, None otherwise
        """
        from sqlalchemy.orm import joinedload
        
        return self.session.query(Constituency).options(
            joinedload(Constituency.candidates)
        ).filter(Constituency.id == constituency_id).first()
    
    def get_constituency_with_voters(self, constituency_id: uuid.UUID) -> Optional[Constituency]:
        """
        Retrieve a constituency with its voters eagerly loaded.
        
        Args:
            constituency_id: Constituency ID to retrieve
            
        Returns:
            Constituency entity with voters if found, None otherwise
        """
        from sqlalchemy.orm import joinedload
        
        return self.session.query(Constituency).options(
            joinedload(Constituency.voters)
        ).filter(Constituency.id == constituency_id).first()
    
    def get_constituency_stats(self, constituency_id: uuid.UUID) -> dict:
        """
        Get statistics for a constituency.
        
        Args:
            constituency_id: Constituency ID to get statistics for
            
        Returns:
            Dictionary with constituency statistics
        """
        constituency = self.get_by_id(constituency_id)
        if constituency is None:
            return {}
        
        # Get voter count
        voter_count = self.session.query(Constituency).join(
            Constituency.voters
        ).filter(
            Constituency.id == constituency_id
        ).count()
        
        # Get candidate count
        candidate_count = self.session.query(Constituency).join(
            Constituency.candidates
        ).filter(
            Constituency.id == constituency_id
        ).count()
        
        # Get polling booth count
        polling_booth_count = self.session.query(Constituency).join(
            Constituency.polling_booths
        ).filter(
            Constituency.id == constituency_id
        ).count()
        
        return {
            'constituency_id': str(constituency_id),
            'name': constituency.name,
            'code': constituency.code,
            'voter_count': voter_count,
            'candidate_count': candidate_count,
            'polling_booth_count': polling_booth_count,
            'created_at': constituency.created_at.isoformat() if constituency.created_at else None
        }
    
    def update_description(self, constituency_id: uuid.UUID, description: str) -> bool:
        """
        Update a constituency's description.
        
        Args:
            constituency_id: Constituency ID to update
            description: New description
            
        Returns:
            True if description was updated, False if constituency not found
        """
        constituency = self.get_by_id(constituency_id)
        if constituency is None:
            return False
        
        constituency.description = description
        self.session.flush()
        return True
    
    def deactivate_constituency(self, constituency_id: uuid.UUID) -> bool:
        """
        Deactivate a constituency by setting deleted_at timestamp.
        
        Args:
            constituency_id: Constituency ID to deactivate
            
        Returns:
            True if constituency was deactivated, False if constituency not found
        """
        constituency = self.get_by_id(constituency_id)
        if constituency is None:
            return False
        
        # Check if constituency is already deactivated
        if constituency.deleted_at is not None:
            return True
        
        # Import here to avoid circular import
        from datetime import datetime
        constituency.deleted_at = datetime.utcnow()
        self.session.flush()
        return True
    
    def activate_constituency(self, constituency_id: uuid.UUID) -> bool:
        """
        Activate a previously deactivated constituency by clearing deleted_at.
        
        Args:
            constituency_id: Constituency ID to activate
            
        Returns:
            True if constituency was activated, False if constituency not found
        """
        constituency = self.get_by_id(constituency_id)
        if constituency is None:
            return False
        
        # Check if constituency is already active
        if constituency.deleted_at is None:
            return True
        
        constituency.deleted_at = None
        self.session.flush()
        return True
    
    def get_all_constituencies_with_stats(self) -> List[dict]:
        """
        Get all constituencies with basic statistics.
        
        Returns:
            List of dictionaries with constituency statistics
        """
        constituencies = self.get_active_constituencies()
        result = []
        
        for constituency in constituencies:
            stats = self.get_constituency_stats(constituency.id)
            result.append(stats)
        
        return result