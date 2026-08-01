"""
Polling booth model representing physical voting locations.

Each polling booth has a unique booth code, is located in a specific constituency,
and has a maximum voter capacity. Booths can be OPEN or CLOSED for voting.
"""

import uuid
from sqlalchemy import String, Integer, CheckConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import db


class PollingBooth(db.Model):
    """
    Physical polling booth/location model.
    
    Attributes:
        id: Unique booth identifier (UUID v4)
        booth_code: Unique alphanumeric booth code (max 20 chars)
        location: Physical address (max 255 chars)
        capacity: Maximum voter capacity (1-10000)
        constituency_id: Foreign key to constituencies table
        status: Booth status ('OPEN' or 'CLOSED')
    
    Relationships:
        constituency: Many-to-one with Constituency
        voting_records: One-to-many with VotingRecord (votes cast at this booth)
    
    Constraints:
        capacity must be between 1 and 10000
    """
    
    __tablename__ = 'polling_booths'
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    
    # Unique booth code
    booth_code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True
    )
    
    # Location information
    location: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    # Capacity with CHECK constraint
    capacity: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    
    # Foreign key
    constituency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('constituencies.id', ondelete='RESTRICT'),
        nullable=False,
        index=True
    )
    
    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='CLOSED',
        server_default='CLOSED'
    )
    
    # Table constraints
    __table_args__ = (
        CheckConstraint(
            'capacity >= 1 AND capacity <= 10000',
            name='polling_booths_capacity_check'
        ),
    )
    
    # Relationships
    constituency: Mapped["Constituency"] = relationship(
        "Constituency",
        back_populates="polling_booths"
    )
    
    voting_records: Mapped[list["VotingRecord"]] = relationship(
        "VotingRecord",
        back_populates="booth",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<PollingBooth(id={self.id}, booth_code='{self.booth_code}', status='{self.status}')>"
