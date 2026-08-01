"""
Voting record repository for database operations on VotingRecord entities.

This module implements the VotingRecordRepository class that provides specialized
database operations for VotingRecord entities.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import uuid
from datetime import datetime, date

from app.models.voting_record import VotingRecord
from .base import BaseRepository


class VotingRecordRepository(BaseRepository[VotingRecord]):
    """
    Repository for VotingRecord entity operations.
    
    Provides specialized queries and operations for VotingRecord entities beyond
    the generic CRUD operations from BaseRepository.
    """
    
    def __init__(self, session: Session):
        """
        Initialize VotingRecordRepository with VotingRecord model class.
        
        Args:
            session: SQLAlchemy database session
        """
        super().__init__(VotingRecord, session)
    
    def get_by_voter(self, voter_id: uuid.UUID) -> Optional[VotingRecord]:
        """
        Retrieve a voting record by voter ID.
        
        Args:
            voter_id: Voter ID to search for
            
        Returns:
            VotingRecord entity if found, None otherwise
        """
        return self.session.query(VotingRecord).filter(
            VotingRecord.voter_id == voter_id
        ).first()
    
    def get_by_candidate(self, candidate_id: uuid.UUID) -> List[VotingRecord]:
        """
        Retrieve all voting records for a specific candidate.
        
        Args:
            candidate_id: Candidate ID to filter by
            
        Returns:
            List of voting records for the specified candidate
        """
        return self.session.query(VotingRecord).filter(
            VotingRecord.candidate_id == candidate_id
        ).all()
    
    def get_by_constituency(self, constituency_id: uuid.UUID) -> List[VotingRecord]:
        """
        Retrieve all voting records in a specific constituency.
        
        Args:
            constituency_id: Constituency ID to filter by
            
        Returns:
            List of voting records in the specified constituency
        """
        # This requires joining with Candidate or Voter to get constituency
        # For now, we'll assume we can query directly if constituency_id is stored
        # In a real implementation, you would join tables
        return self.session.query(VotingRecord).filter(
            VotingRecord.constituency_id == constituency_id
        ).all()
    
    def get_by_polling_booth(self, polling_booth_id: uuid.UUID) -> List[VotingRecord]:
        """
        Retrieve all voting records from a specific polling booth.
        
        Args:
            polling_booth_id: Polling booth ID to filter by
            
        Returns:
            List of voting records from the specified polling booth
        """
        return self.session.query(VotingRecord).filter(
            VotingRecord.polling_booth_id == polling_booth_id
        ).all()
    
    def voter_has_voted(self, voter_id: uuid.UUID) -> bool:
        """
        Check if a voter has already voted.
        
        Args:
            voter_id: Voter ID to check
            
        Returns:
            True if voter has voted, False otherwise
        """
        return self.get_by_voter(voter_id) is not None
    
    def get_voting_record_with_details(self, voting_record_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """
        Retrieve a voting record with voter, candidate, and polling booth details.
        
        Args:
            voting_record_id: Voting record ID to retrieve
            
        Returns:
            Dictionary with voting record details if found, None otherwise
        """
        from sqlalchemy.orm import joinedload
        
        voting_record = self.session.query(VotingRecord).options(
            joinedload(VotingRecord.voter),
            joinedload(VotingRecord.candidate),
            joinedload(VotingRecord.polling_booth)
        ).filter(VotingRecord.id == voting_record_id).first()
        
        if voting_record is None:
            return None
        
        return {
            'id': str(voting_record.id),
            'voter_id': str(voting_record.voter_id),
            'voter_name': voting_record.voter.full_name if voting_record.voter else None,
            'candidate_id': str(voting_record.candidate_id),
            'candidate_name': voting_record.candidate.full_name if voting_record.candidate else None,
            'candidate_party': voting_record.candidate.party if voting_record.candidate else None,
            'polling_booth_id': str(voting_record.polling_booth_id),
            'polling_booth_code': voting_record.polling_booth.code if voting_record.polling_booth else None,
            'constituency_id': str(voting_record.constituency_id),
            'voted_at': voting_record.voted_at.isoformat() if voting_record.voted_at else None,
            'status': voting_record.status
        }
    
    def get_vote_count_by_candidate(self, candidate_id: uuid.UUID) -> int:
        """
        Get the total vote count for a specific candidate.
        
        Args:
            candidate_id: Candidate ID to count votes for
            
        Returns:
            Number of votes for the candidate
        """
        return self.session.query(VotingRecord).filter(
            VotingRecord.candidate_id == candidate_id,
            VotingRecord.status == 'COMPLETED'
        ).count()
    
    def get_vote_count_by_constituency(self, constituency_id: uuid.UUID) -> int:
        """
        Get the total vote count in a specific constituency.
        
        Args:
            constituency_id: Constituency ID to count votes for
            
        Returns:
            Number of votes in the constituency
        """
        return self.session.query(VotingRecord).filter(
            VotingRecord.constituency_id == constituency_id,
            VotingRecord.status == 'COMPLETED'
        ).count()
    
    def get_vote_count_by_polling_booth(self, polling_booth_id: uuid.UUID) -> int:
        """
        Get the total vote count from a specific polling booth.
        
        Args:
            polling_booth_id: Polling booth ID to count votes for
            
        Returns:
            Number of votes from the polling booth
        """
        return self.session.query(VotingRecord).filter(
            VotingRecord.polling_booth_id == polling_booth_id,
            VotingRecord.status == 'COMPLETED'
        ).count()
    
    def get_voting_results_by_constituency(self, constituency_id: uuid.UUID) -> List[Dict[str, Any]]:
        """
        Get voting results by candidate for a specific constituency.
        
        Args:
            constituency_id: Constituency ID to get results for
            
        Returns:
            List of dictionaries with candidate vote counts
        """
        # This query groups votes by candidate within a constituency
        results = self.session.query(
            VotingRecord.candidate_id,
            func.count(VotingRecord.id).label('vote_count')
        ).filter(
            VotingRecord.constituency_id == constituency_id,
            VotingRecord.status == 'COMPLETED'
        ).group_by(
            VotingRecord.candidate_id
        ).all()
        
        return [
            {
                'candidate_id': str(candidate_id),
                'vote_count': vote_count
            }
            for candidate_id, vote_count in results
        ]
    
    def get_voting_timeline(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """
        Get voting activity timeline (votes per day).
        
        Args:
            start_date: Start date for timeline
            end_date: End date for timeline
            
        Returns:
            List of dictionaries with date and vote count
        """
        results = self.session.query(
            func.date(VotingRecord.voted_at).label('vote_date'),
            func.count(VotingRecord.id).label('vote_count')
        ).filter(
            and_(
                func.date(VotingRecord.voted_at) >= start_date,
                func.date(VotingRecord.voted_at) <= end_date,
                VotingRecord.status == 'COMPLETED'
            )
        ).group_by(
            func.date(VotingRecord.voted_at)
        ).order_by(
            func.date(VotingRecord.voted_at)
        ).all()
        
        return [
            {
                'date': vote_date.isoformat(),
                'vote_count': vote_count
            }
            for vote_date, vote_count in results
        ]
    
    def get_voting_stats(self) -> Dict[str, Any]:
        """
        Get overall voting statistics.
        
        Returns:
            Dictionary with voting statistics
        """
        total_votes = self.session.query(VotingRecord).filter(
            VotingRecord.status == 'COMPLETED'
        ).count()
        
        # Get votes by status
        status_counts = self.session.query(
            VotingRecord.status,
            func.count(VotingRecord.id).label('count')
        ).group_by(VotingRecord.status).all()
        
        # Get today's votes
        today = date.today()
        today_votes = self.session.query(VotingRecord).filter(
            and_(
                func.date(VotingRecord.voted_at) == today,
                VotingRecord.status == 'COMPLETED'
            )
        ).count()
        
        return {
            'total_votes': total_votes,
            'today_votes': today_votes,
            'status_counts': {status: count for status, count in status_counts}
        }
    
    def update_status(self, voting_record_id: uuid.UUID, status: str) -> bool:
        """
        Update a voting record's status.
        
        Args:
            voting_record_id: Voting record ID to update
            status: New status (must be valid status)
            
        Returns:
            True if status was updated, False if voting record not found or invalid status
        """
        # Validate status
        valid_statuses = ['QUEUED', 'PROCESSING', 'COMPLETED', 'FAILED']
        if status not in valid_statuses:
            return False
        
        voting_record = self.get_by_id(voting_record_id)
        if voting_record is None:
            return False
        
        # Check if status is already set to the new value
        if voting_record.status == status:
            return True
        
        voting_record.status = status
        self.session.flush()
        return True
    
    def mark_as_completed(self, voting_record_id: uuid.UUID) -> bool:
        """
        Mark a voting record as completed.
        
        Args:
            voting_record_id: Voting record ID to mark as completed
            
        Returns:
            True if status was updated, False otherwise
        """
        return self.update_status(voting_record_id, 'COMPLETED')
    
    def mark_as_failed(self, voting_record_id: uuid.UUID) -> bool:
        """
        Mark a voting record as failed.
        
        Args:
            voting_record_id: Voting record ID to mark as failed
            
        Returns:
            True if status was updated, False otherwise
        """
        return self.update_status(voting_record_id, 'FAILED')
    
    def get_failed_voting_records(self, limit: int = 100) -> List[VotingRecord]:
        """
        Retrieve failed voting records for review.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of failed voting records
        """
        return self.session.query(VotingRecord).filter(
            VotingRecord.status == 'FAILED'
        ).limit(limit).all()
    
    def get_pending_voting_records(self, limit: int = 100) -> List[VotingRecord]:
        """
        Retrieve pending voting records (QUEUED or PROCESSING status).
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of pending voting records
        """
        return self.session.query(VotingRecord).filter(
            or_(
                VotingRecord.status == 'QUEUED',
                VotingRecord.status == 'PROCESSING'
            )
        ).limit(limit).all()
    
    def delete_by_voter(self, voter_id: uuid.UUID) -> bool:
        """
        Delete voting record by voter ID.
        
        Args:
            voter_id: Voter ID to delete voting record for
            
        Returns:
            True if voting record was deleted, False otherwise
        """
        voting_record = self.get_by_voter(voter_id)
        if voting_record is None:
            return False
        
        self.session.delete(voting_record)
        self.session.flush()
        return True