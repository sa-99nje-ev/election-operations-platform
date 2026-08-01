"""
Voting record model representing individual votes cast.

This is the core model for vote storage. Each record links a voter to a candidate
and booth with a timestamp. The UNIQUE constraint on voter_id is CRITICAL for
preventing duplicate votes - it's the primary mechanism enforcing one-vote-per-voter.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.extensions import db


class VotingRecord(db.Model):
    """
    Individual vote record model.
    
    Attributes:
        id: Unique vote identifier (UUID v4)
        voter_id: Foreign key to voters table (UNIQUE - prevents duplicate votes)
        candidate_id: Foreign key to candidates table
        booth_id: Foreign key to polling_booths table
        voted_at: Vote timestamp (timezone-aware)
    
    Relationships:
        voter: Many-to-one with Voter
        candidate: Many-to-one with Candidate
        booth: Many-to-one with PollingBooth
    
    Critical Constraints:
        UNIQUE constraint on voter_id prevents duplicate votes.
        When a second vote attempt occurs, PostgreSQL raises IntegrityError,
        causing transaction rollback and preventing the duplicate vote.
    """
    
    __tablename__ = 'voting_records'
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    
    # Foreign keys - voter_id is UNIQUE (critical for duplicate prevention)
    voter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('voters.id', ondelete='RESTRICT'),
        unique=True,  # CRITICAL: Prevents duplicate votes
        nullable=False,
        index=True
    )
    
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('candidates.id', ondelete='RESTRICT'),
        nullable=False,
        index=True
    )
    
    booth_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('polling_booths.id', ondelete='RESTRICT'),
        nullable=False,
        index=True
    )
    
    # Timestamp
    voted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    
    # Table indexes
    __table_args__ = (
        # Composite index for per-booth results aggregation
        Index('idx_voting_records_candidate_booth', 'candidate_id', 'booth_id'),
    )
    
    # Relationships
    voter: Mapped["Voter"] = relationship(
        "Voter",
        back_populates="voting_records"
    )
    
    candidate: Mapped["Candidate"] = relationship(
        "Candidate",
        back_populates="voting_records"
    )
    
    booth: Mapped["PollingBooth"] = relationship(
        "PollingBooth",
        back_populates="voting_records"
    )
    
    def __repr__(self) -> str:
        return f"<VotingRecord(id={self.id}, voter_id={self.voter_id}, candidate_id={self.candidate_id}, voted_at={self.voted_at})>"
