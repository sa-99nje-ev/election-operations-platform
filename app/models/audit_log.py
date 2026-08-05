"""
Audit log model for security and compliance tracking.

This append-only table records all significant events in the system including
login attempts, vote submissions, and administrative actions. Each entry captures
who did what, when, and from where, with millisecond-precision timestamps.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base


class AuditLog(Base):
    """
    Security audit log model (append-only).
    
    Attributes:
        id: Unique log entry identifier (UUID v4)
        event_type: Event category (e.g., 'login', 'vote_submitted', max 50 chars)
        actor_id: Foreign key to users table (who performed the action)
        target_id: Optional UUID of affected resource (voter_id, candidate_id, etc.)
        outcome: Event outcome ('success' or 'failure', max 20 chars)
        ip_address: Source IP address (supports IPv6, max 45 chars)
        created_at: Event timestamp with millisecond precision (timezone-aware)
    
    Relationships:
        actor: Many-to-one with User (user who performed the action)
    
    Important Notes:
        - This is an APPEND-ONLY table
        - No UPDATE or DELETE operations via API
        - Used for security audits and compliance reporting
    """
    
    __tablename__ = 'audit_logs'
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    
    # Event information
    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )
    
    # Actor (who performed the action)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='RESTRICT'),
        nullable=True,
        index=True
    )
    
    # Target (what was affected)
    target_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True
    )
    
    # Outcome and context
    outcome: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )
    
    ip_address: Mapped[str | None] = mapped_column(
        String(45),  # Supports IPv6
        nullable=True
    )
    
    # Timestamp with millisecond precision
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True
    )
    
    # Table indexes for common query patterns
    __table_args__ = (
        Index('idx_audit_logs_event_actor', 'event_type', 'actor_id'),
        Index('idx_audit_logs_created_at', 'created_at'),
    )
    
    # Relationships
    actor: Mapped["User"] = relationship(
        "User",
        back_populates="audit_logs"
    )
    
    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, event_type='{self.event_type}', outcome='{self.outcome}', created_at={self.created_at})>"
