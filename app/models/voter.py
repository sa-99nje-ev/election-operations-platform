"""
Registered voter model.
"""

import uuid
from datetime import date
from sqlalchemy import String, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Voter(Base):
    __tablename__ = 'voters'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    national_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    full_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    dob: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )
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
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='active',
        server_default='active'
    )

    # All relationships required by back_populates across other models
    constituency: Mapped["Constituency"] = relationship(
        "Constituency",
        back_populates="voters"
    )

    user: Mapped["User | None"] = relationship(
        "User",
        back_populates="voters"
    )

    voting_records: Mapped[list["VotingRecord"]] = relationship(
        "VotingRecord",
        back_populates="voter",
        cascade="all, delete-orphan"
    )