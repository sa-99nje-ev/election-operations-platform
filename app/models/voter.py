"""
Voter model representing registered voters.

Each voter has a unique national ID, is assigned to a constituency, and may
optionally have an associated user account. The model tracks voter status
(active/inactive) for eligibility verification.
"""

import uuid
from datetime import date
from sqlalchemy import String, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import db


class Voter(db.Model):
    """
    Registered voter model.
    
    Attributes:
        id: Unique voter identifier (UUID v4)
        national_id: Unique government-issued ID (max 50 chars)
        full_name: Voter's full name (max 100 chars)
        dob: Date of birth
        constituency_id: Foreign key to constituencies table
        user_id: Optional foreign key to users table
        status: Voter status ('active' or 'inactive')
    
    Relationships:
        constituency: Many-to-one with Constituency
        user: Many-to-one with User (optional)
        voting_records: One-to-many with VotingRecord (votes cast by this voter)
    """
    
    __tablename__ = 'voters'
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    
    # Unique national ID
    national_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    
    # Personal information
    full_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    
    dob: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )
    
    # Foreign keys
    constituency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('constituencies.id', ondelete='RESTRICT'),
        nullable=False,
        index=True
    )
    
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='RESTRICT'),
        nullable=True,
        index=True
    )
    
    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='active',
        server_default='active'
    )
    
    # Relationships
    constituency: Mapped["Constituency"] = relationship(
        "Constituency",
        back_populates="voters"
    )
    
    user: Mapped["User"] = relationship(
        "User",
        back_populates="voters"
    )
    
    voting_records: Mapped[list["VotingRecord"]] = relationship(
        "VotingRecord",
        back_populates="voter",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Voter(id={self.id}, national_id='{self.national_id}', full_name='{self.full_name}')>"
