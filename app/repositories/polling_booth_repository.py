"""
Polling booth repository for database operations on PollingBooth entities.

This module implements the PollingBoothRepository class that provides specialized
database operations for PollingBooth entities.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
import uuid

from app.models.polling_booth import PollingBooth
from .base import BaseRepository


class PollingBoothRepository(BaseRepository[PollingBooth]):
    """
    Repository for PollingBooth entity operations.
    
    Provides specialized queries and operations for PollingBooth entities beyond
    the generic CRUD operations from BaseRepository.
    """
    
    def __init__(self, session: Session):
        """
        Initialize PollingBoothRepository with PollingBooth model class.
        
        Args:
            session: SQLAlchemy database session
        """
        super().__init__(PollingBooth, session)
    
    def get_by_code(self, code: str) -> Optional[PollingBooth]:
        """
        Retrieve a polling booth by code.
        
        Args:
            code: Polling booth code to search for
            
        Returns:
            PollingBooth entity if found, None otherwise
        """
        return self.session.query(PollingBooth).filter(
            PollingBooth.code == code
        ).first()
    
    def get_by_constituency(self, constituency_id: uuid.UUID) -> List[PollingBooth]:
        """
        Retrieve all polling booths in a specific constituency.
        
        Args:
            constituency_id: Constituency ID to filter by
            
        Returns:
            List of polling booths in the specified constituency
        """
        return self.session.query(PollingBooth).filter(
            PollingBooth.constituency_id == constituency_id
        ).all()
    
    def get_by_status(self, status: str, constituency_id: Optional[uuid.UUID] = None) -> List[PollingBooth]:
        """
        Retrieve polling booths by status.
        
        Args:
            status: Polling booth status (OPEN, CLOSED, etc.)
            constituency_id: Optional constituency ID to filter by
            
        Returns:
            List of polling booths with the specified status
        """
        query = self.session.query(PollingBooth).filter(
            PollingBooth.status == status
        )
        
        if constituency_id:
            query = query.filter(PollingBooth.constituency_id == constituency_id)
        
        return query.all()
    
    def get_open_polling_booths(self, constituency_id: Optional[uuid.UUID] = None) -> List[PollingBooth]:
        """
        Retrieve all open polling booths.
        
        Args:
            constituency_id: Optional constituency ID to filter by
            
        Returns:
            List of open polling booths
        """
        return self.get_by_status('OPEN', constituency_id)
    
    def get_closed_polling_booths(self, constituency_id: Optional[uuid.UUID] = None) -> List[PollingBooth]:
        """
        Retrieve all closed polling booths.
        
        Args:
            constituency_id: Optional constituency ID to filter by
            
        Returns:
            List of closed polling booths
        """
        return self.get_by_status('CLOSED', constituency_id)
    
    def get_active_polling_booths(self) -> List[PollingBooth]:
        """
        Retrieve all active polling booths (without deleted_at timestamp).
        
        Returns:
            List of active polling booths
        """
        return self.session.query(PollingBooth).filter(
            PollingBooth.deleted_at.is_(None)
        ).all()
    
    def search_polling_booths(
        self,
        search_term: str,
        constituency_id: Optional[uuid.UUID] = None
    ) -> List[PollingBooth]:
        """
        Search polling booths by code or location name (partial match, case-insensitive).
        
        Args:
            search_term: Search term to match against codes or location names
            constituency_id: Optional constituency ID to filter by
            
        Returns:
            List of polling booths matching the search criteria
        """
        query = self.session.query(PollingBooth).filter(
            or_(
                PollingBooth.code.ilike(f'%{search_term}%'),
                PollingBooth.location_name.ilike(f'%{search_term}%')
            ),
            PollingBooth.deleted_at.is_(None)
        )
        
        if constituency_id:
            query = query.filter(PollingBooth.constituency_id == constituency_id)
        
        return query.all()
    
    def code_exists(
        self,
        code: str,
        exclude_polling_booth_id: Optional[uuid.UUID] = None
    ) -> bool:
        """
        Check if a polling booth code already exists.
        
        Args:
            code: Polling booth code to check
            exclude_polling_booth_id: Optional polling booth ID to exclude from check
            
        Returns:
            True if code exists, False otherwise
        """
        query = self.session.query(PollingBooth).filter(
            PollingBooth.code == code
        )
        
        if exclude_polling_booth_id:
            query = query.filter(PollingBooth.id != exclude_polling_booth_id)
        
        return query.first() is not None
    
    def get_polling_booth_with_constituency(self, polling_booth_id: uuid.UUID) -> Optional[PollingBooth]:
        """
        Retrieve a polling booth with its constituency eagerly loaded.
        
        Args:
            polling_booth_id: Polling booth ID to retrieve
            
        Returns:
            PollingBooth entity with constituency if found, None otherwise
        """
        from sqlalchemy.orm import joinedload
        
        return self.session.query(PollingBooth).options(
            joinedload(PollingBooth.constituency)
        ).filter(PollingBooth.id == polling_booth_id).first()
    
    def get_polling_booth_with_voters(self, polling_booth_id: uuid.UUID) -> Optional[PollingBooth]:
        """
        Retrieve a polling booth with its assigned voters eagerly loaded.
        
        Args:
            polling_booth_id: Polling booth ID to retrieve
            
        Returns:
            PollingBooth entity with voters if found, None otherwise
        """
        from sqlalchemy.orm import joinedload
        
        return self.session.query(PollingBooth).options(
            joinedload(PollingBooth.voters)
        ).filter(PollingBooth.id == polling_booth_id).first()
    
    def get_polling_booth_stats(self, polling_booth_id: uuid.UUID) -> dict:
        """
        Get statistics for a polling booth.
        
        Args:
            polling_booth_id: Polling booth ID to get statistics for
            
        Returns:
            Dictionary with polling booth statistics
        """
        polling_booth = self.get_by_id(polling_booth_id)
        if polling_booth is None:
            return {}
        
        # Get voter count
        voter_count = self.session.query(PollingBooth).join(
            PollingBooth.voters
        ).filter(
            PollingBooth.id == polling_booth_id
        ).count()
        
        return {
            'polling_booth_id': str(polling_booth_id),
            'code': polling_booth.code,
            'location_name': polling_booth.location_name,
            'status': polling_booth.status,
            'capacity': polling_booth.capacity,
            'voter_count': voter_count,
            'utilization_percentage': (voter_count / polling_booth.capacity * 100) if polling_booth.capacity > 0 else 0,
            'created_at': polling_booth.created_at.isoformat() if polling_booth.created_at else None
        }
    
    def update_status(self, polling_booth_id: uuid.UUID, status: str) -> bool:
        """
        Update a polling booth's status.
        
        Args:
            polling_booth_id: Polling booth ID to update
            status: New status (must be valid status)
            
        Returns:
            True if status was updated, False if polling booth not found or invalid status
        """
        # Validate status
        valid_statuses = ['OPEN', 'CLOSED']
        if status not in valid_statuses:
            return False
        
        polling_booth = self.get_by_id(polling_booth_id)
        if polling_booth is None:
            return False
        
        # Check if status is already set to the new value
        if polling_booth.status == status:
            return True
        
        polling_booth.status = status
        self.session.flush()
        return True
    
    def open_polling_booth(self, polling_booth_id: uuid.UUID) -> bool:
        """
        Open a polling booth (set status to OPEN).
        
        Args:
            polling_booth_id: Polling booth ID to open
            
        Returns:
            True if polling booth was opened, False otherwise
        """
        return self.update_status(polling_booth_id, 'OPEN')
    
    def close_polling_booth(self, polling_booth_id: uuid.UUID) -> bool:
        """
        Close a polling booth (set status to CLOSED).
        
        Args:
            polling_booth_id: Polling booth ID to close
            
        Returns:
            True if polling booth was closed, False otherwise
        """
        return self.update_status(polling_booth_id, 'CLOSED')
    
    def update_capacity(self, polling_booth_id: uuid.UUID, capacity: int) -> bool:
        """
        Update a polling booth's capacity.
        
        Args:
            polling_booth_id: Polling booth ID to update
            capacity: New capacity (must be positive)
            
        Returns:
            True if capacity was updated, False if polling booth not found or invalid capacity
        """
        if capacity <= 0:
            return False
        
        polling_booth = self.get_by_id(polling_booth_id)
        if polling_booth is None:
            return False
        
        polling_booth.capacity = capacity
        self.session.flush()
        return True
    
    def deactivate_polling_booth(self, polling_booth_id: uuid.UUID) -> bool:
        """
        Deactivate a polling booth by setting deleted_at timestamp.
        
        Args:
            polling_booth_id: Polling booth ID to deactivate
            
        Returns:
            True if polling booth was deactivated, False if polling booth not found
        """
        polling_booth = self.get_by_id(polling_booth_id)
        if polling_booth is None:
            return False
        
        # Check if polling booth is already deactivated
        if polling_booth.deleted_at is not None:
            return True
        
        # Import here to avoid circular import
        from datetime import datetime
        polling_booth.deleted_at = datetime.utcnow()
        self.session.flush()
        return True
    
    def activate_polling_booth(self, polling_booth_id: uuid.UUID) -> bool:
        """
        Activate a previously deactivated polling booth by clearing deleted_at.
        
        Args:
            polling_booth_id: Polling booth ID to activate
            
        Returns:
            True if polling booth was activated, False if polling booth not found
        """
        polling_booth = self.get_by_id(polling_booth_id)
        if polling_booth is None:
            return False
        
        # Check if polling booth is already active
        if polling_booth.deleted_at is None:
            return True
        
        polling_booth.deleted_at = None
        self.session.flush()
        return True
    
    def get_polling_booths_by_capacity_range(
        self,
        min_capacity: Optional[int] = None,
        max_capacity: Optional[int] = None,
        constituency_id: Optional[uuid.UUID] = None
    ) -> List[PollingBooth]:
        """
        Retrieve polling booths within a specific capacity range.
        
        Args:
            min_capacity: Minimum capacity (inclusive)
            max_capacity: Maximum capacity (inclusive)
            constituency_id: Optional constituency ID to filter by
            
        Returns:
            List of polling booths within the specified capacity range
        """
        query = self.session.query(PollingBooth)
        
        if min_capacity is not None:
            query = query.filter(PollingBooth.capacity >= min_capacity)
        
        if max_capacity is not None:
            query = query.filter(PollingBooth.capacity <= max_capacity)
        
        if constituency_id:
            query = query.filter(PollingBooth.constituency_id == constituency_id)
        
        return query.all()