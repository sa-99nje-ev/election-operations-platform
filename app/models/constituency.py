"""
Constituency model representing electoral districts.

Each constituency is a geographic region that elects one representative.
Constituencies contain voters, candidates competing for election, and polling booths.
"""

import uuid
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import db


class Constituency(db.Model):
    """
    Electoral constituency/district model.
    
    Attributes:
        id: Unique constituency identifier (UUID v4)
        name: Unique constituency name (max 100 chars)
        region: Geographic region (max 100 chars)
    
    Relationships:
        voters: One-to-many with Voter (voters registered in this constituency)
        candidates: One-to-many with Candidate (candidates contesting in this constituency)
        polling_booths: One-to-many with PollingBooth (booths serving this constituency)
    """
    
    __tablename__ = 'constituencies'
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    
    # Unique constituency name
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )
    
    # Geographic region
    region: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    
    # Relationships
    voters: Mapped[list["Voter"]] = relationship(
        "Voter",
        back_populates="constituency",
        cascade="all, delete-orphan"
    )
    
    candidates: Mapped[list["Candidate"]] = relationship(
        "Candidate",
        back_populates="constituency",
        cascade="all, delete-orphan"
    )
    
    polling_booths: Mapped[list["PollingBooth"]] = relationship(
        "PollingBooth",
        back_populates="constituency",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Constituency(id={self.id}, name='{self.name}', region='{self.region}')>"
