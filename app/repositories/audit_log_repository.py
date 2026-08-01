"""
Audit log repository for database operations on AuditLog entities.

This module implements the AuditLogRepository class that provides specialized
database operations for AuditLog entities for comprehensive logging and auditing.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import uuid
from datetime import datetime, date, timedelta

from app.models.audit_log import AuditLog
from .base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    """
    Repository for AuditLog entity operations.
    
    Provides specialized queries and operations for AuditLog entities beyond
    the generic CRUD operations from BaseRepository.
    """
    
    def __init__(self, session: Session):
        """
        Initialize AuditLogRepository with AuditLog model class.
        
        Args:
            session: SQLAlchemy database session
        """
        super().__init__(AuditLog, session)
    
    def get_by_event_type(self, event_type: str) -> List[AuditLog]:
        """
        Retrieve audit logs by event type.
        
        Args:
            event_type: Event type to filter by
            
        Returns:
            List of audit logs with the specified event type
        """
        return self.session.query(AuditLog).filter(
            AuditLog.event_type == event_type
        ).all()
    
    def get_by_actor(self, actor_id: uuid.UUID) -> List[AuditLog]:
        """
        Retrieve audit logs by actor ID.
        
        Args:
            actor_id: Actor user ID to filter by
            
        Returns:
            List of audit logs performed by the specified actor
        """
        return self.session.query(AuditLog).filter(
            AuditLog.actor_id == actor_id
        ).all()
    
    def get_by_target_id(self, target_id: uuid.UUID) -> List[AuditLog]:
        """
        Retrieve audit logs by target ID.
        
        Args:
            target_id: Target ID to filter by
            
        Returns:
            List of audit logs targeting the specified resource
        """
        return self.session.query(AuditLog).filter(
            AuditLog.target_id == target_id
        ).all()
    
    def get_by_time_range(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> List[AuditLog]:
        """
        Retrieve audit logs within a specific time range.
        
        Args:
            start_time: Start time (inclusive)
            end_time: End time (inclusive)
            
        Returns:
            List of audit logs within the specified time range
        """
        return self.session.query(AuditLog).filter(
            and_(
                AuditLog.created_at >= start_time,
                AuditLog.created_at <= end_time
            )
        ).all()
    
    def search_logs(
        self,
        search_term: str,
        event_type: Optional[str] = None,
        actor_id: Optional[uuid.UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[AuditLog]:
        """
        Search audit logs with multiple criteria.
        
        Args:
            search_term: Search term to match against details or ip_address
            event_type: Optional event type to filter by
            actor_id: Optional actor ID to filter by
            start_time: Optional start time for time range filter
            end_time: Optional end time for time range filter
            
        Returns:
            List of audit logs matching the search criteria
        """
        query = self.session.query(AuditLog)
        
        # Apply search term filter
        if search_term:
            query = query.filter(
                or_(
                    AuditLog.details.ilike(f'%{search_term}%'),
                    AuditLog.ip_address.ilike(f'%{search_term}%')
                )
            )
        
        # Apply event type filter
        if event_type:
            query = query.filter(AuditLog.event_type == event_type)
        
        # Apply actor ID filter
        if actor_id:
            query = query.filter(AuditLog.actor_id == actor_id)
        
        # Apply time range filter
        if start_time:
            query = query.filter(AuditLog.created_at >= start_time)
        
        if end_time:
            query = query.filter(AuditLog.created_at <= end_time)
        
        return query.order_by(AuditLog.created_at.desc()).all()
    
    def get_recent_logs(self, limit: int = 100) -> List[AuditLog]:
        """
        Retrieve recent audit logs.
        
        Args:
            limit: Maximum number of logs to return
            
        Returns:
            List of recent audit logs
        """
        return self.session.query(AuditLog).order_by(
            AuditLog.created_at.desc()
        ).limit(limit).all()
    
    def get_logs_by_outcome(self, outcome: str) -> List[AuditLog]:
        """
        Retrieve audit logs by outcome.
        
        Args:
            outcome: Outcome to filter by (success, failure)
            
        Returns:
            List of audit logs with the specified outcome
        """
        return self.session.query(AuditLog).filter(
            AuditLog.outcome == outcome
        ).all()
    
    def get_log_with_actor(self, log_id: uuid.UUID) -> Optional[AuditLog]:
        """
        Retrieve an audit log with its actor eagerly loaded.
        
        Args:
            log_id: Audit log ID to retrieve
            
        Returns:
            AuditLog entity with actor if found, None otherwise
        """
        from sqlalchemy.orm import joinedload
        
        return self.session.query(AuditLog).options(
            joinedload(AuditLog.actor)
        ).filter(AuditLog.id == log_id).first()
    
    def get_audit_stats(self) -> Dict[str, Any]:
        """
        Get audit log statistics.
        
        Returns:
            Dictionary with audit statistics
        """
        # Total logs
        total_logs = self.session.query(AuditLog).count()
        
        # Logs by event type
        logs_by_event_type = self.session.query(
            AuditLog.event_type,
            func.count(AuditLog.id).label('log_count')
        ).group_by(AuditLog.event_type).all()
        
        # Logs by outcome
        logs_by_outcome = self.session.query(
            AuditLog.outcome,
            func.count(AuditLog.id).label('log_count')
        ).group_by(AuditLog.outcome).all()
        
        # Logs by actor
        logs_by_actor = self.session.query(
            AuditLog.actor_id,
            func.count(AuditLog.id).label('log_count')
        ).group_by(AuditLog.actor_id).all()
        
        # Recent activity (last 24 hours)
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        recent_activity = self.session.query(AuditLog).filter(
            AuditLog.timestamp >= twenty_four_hours_ago
        ).count()
        
        return {
            'total_logs': total_logs,
            'recent_activity_24h': recent_activity,
            'logs_by_event_type': {
                event_type: log_count
                for event_type, log_count in logs_by_event_type
            },
            'logs_by_outcome': {
                outcome: log_count
                for outcome, log_count in logs_by_outcome
            },
            'logs_by_actor': [
                {'actor_id': str(actor_id), 'log_count': log_count}
                for actor_id, log_count in logs_by_actor
            ]
        }
    
    def get_daily_activity(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get daily audit log activity for the specified number of days.
        
        Args:
            days: Number of days to include in the report
            
        Returns:
            List of dictionaries with date and activity count
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        results = self.session.query(
            func.date(AuditLog.created_at).label('log_date'),
            func.count(AuditLog.id).label('log_count')
        ).filter(
            and_(
                func.date(AuditLog.created_at) >= start_date,
                func.date(AuditLog.created_at) <= end_date
            )
        ).group_by(
            func.date(AuditLog.created_at)
        ).order_by(
            func.date(AuditLog.created_at)
        ).all()
        
        return [
            {
                'date': log_date.isoformat(),
                'log_count': log_count
            }
            for log_date, log_count in results
        ]
    
    def create_audit_log(
        self,
        event_type: str,
        actor_id: Optional[uuid.UUID],
        target_id: Optional[uuid.UUID],
        outcome: str,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        """
        Create a new audit log entry.
        
        Args:
            event_type: Type of event being logged
            actor_id: ID of the user performing the action
            target_id: ID of the resource being acted upon
            outcome: Outcome of the action (success, failure)
            ip_address: Optional IP address of the client
            
        Returns:
            Created AuditLog entity
        """
        # Validate outcome
        valid_outcomes = ['success', 'failure']
        if outcome not in valid_outcomes:
            raise ValueError(f"Invalid outcome: {outcome}. Must be one of: {valid_outcomes}")
        
        # Create new audit log
        audit_log = AuditLog(
            event_type=event_type,
            actor_id=actor_id,
            target_id=target_id,
            outcome=outcome,
            ip_address=ip_address,
            created_at=datetime.utcnow()
        )
        
        self.session.add(audit_log)
        self.session.flush()
        
        return audit_log
    
    def log_user_login(
        self,
        user_id: uuid.UUID,
        outcome: str,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        """
        Log a user login attempt.
        
        Args:
            user_id: User ID attempting to login
            outcome: Outcome of the login attempt (success, failure)
            ip_address: Optional IP address of the client
            
        Returns:
            Created AuditLog entity
        """
        return self.create_audit_log(
            event_type='USER_LOGIN',
            actor_id=user_id,
            target_id=user_id,
            outcome=outcome,
            ip_address=ip_address
        )
    
    def log_user_logout(
        self,
        user_id: uuid.UUID,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        """
        Log a user logout.
        
        Args:
            user_id: User ID logging out
            ip_address: Optional IP address of the client
            
        Returns:
            Created AuditLog entity
        """
        return self.create_audit_log(
            event_type='USER_LOGOUT',
            actor_id=user_id,
            target_id=user_id,
            outcome='success',
            ip_address=ip_address
        )
    
    def log_vote_submission(
        self,
        voter_id: uuid.UUID,
        candidate_id: uuid.UUID,
        outcome: str,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        """
        Log a vote submission.
        
        Args:
            voter_id: Voter ID submitting the vote
            candidate_id: Candidate ID being voted for
            outcome: Outcome of the vote submission (success, failure)
            ip_address: Optional IP address of the client
            
        Returns:
            Created AuditLog entity
        """
        return self.create_audit_log(
            event_type='VOTE_SUBMISSION',
            actor_id=voter_id,
            target_id=candidate_id,
            outcome=outcome,
            ip_address=ip_address
        )
    
    def cleanup_old_logs(self, days_to_keep: int = 90) -> int:
        """
        Delete audit logs older than the specified number of days.
        
        Args:
            days_to_keep: Number of days to keep logs
            
        Returns:
            Number of logs deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        # Find old logs
        old_logs = self.session.query(AuditLog).filter(
            AuditLog.created_at < cutoff_date
        ).all()
        
        deleted_count = 0
        for log in old_logs:
            self.session.delete(log)
            deleted_count += 1
        
        if deleted_count > 0:
            self.session.flush()
        
        return deleted_count