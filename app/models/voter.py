from __future__ import annotations
import uuid
from datetime import date
from typing import TYPE_CHECKING
from sqlalchemy import String, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.constituency import Constituency
    from app.models.user import User
    from app.models.voting_record import VotingRecord


class Voter(Base):
    __tablename__ = "voters"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    national_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    dob: Mapped[date] = mapped_column(Date, nullable=False)
    constituency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("constituencies.id", ondelete="RESTRICT"),
        nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True
    )
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)

    constituency: Mapped["Constituency"] = relationship("Constituency", back_populates="voters")
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    voting_records: Mapped[list["VotingRecord"]] = relationship("VotingRecord", back_populates="voter")
