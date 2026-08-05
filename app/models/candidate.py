"""
Candidate model representing election candidates.

Each candidate has a unique national ID, is associated with a political party,
and contests in a specific constituency. Candidates may optionally have a user
account for platform access.
"""

import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Candidate(Base):
    """
    Election candidate model.
    
    Attributes:
        id: Unique candidate identifier (UUID v4)
        national_id: Unique government-issued ID (max 50 chars)
        full_name: Candidate's full name (max 100 chars)
        party: Political party affiliation (max 100 chars)
        constituency_id: Foreign key to constituencies table
        user_id: Optional foreign key to users table
    
    Relationships:
        constituency: Many-to-one with Constituency
        user: Many-to-one with User (optional)
        voting_records: One-to-many with VotingRecord (votes received by this candidate)
    """
    
    __tablename__ = 'candidates'
    
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
    
    # Political affiliation
    party: Mapped[str] = mapped_column(
        String(100),
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
    
    # Relationships
    constituency: Mapped["Constituency"] = relationship(
        "Constituency",
        back_populates="candidates"
    )
    
    user: Mapped["User"] = relationship(
        "User",
        back_populates="candidates"
    )
    
    voting_records: Mapped[list["VotingRecord"]] = relationship(
        "VotingRecord",
        back_populates="candidate",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Candidate(id={self.id}, national_id='{self.national_id}', full_name='{self.full_name}', party='{self.party}')>"
