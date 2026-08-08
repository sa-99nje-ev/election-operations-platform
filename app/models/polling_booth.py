from __future__ import annotations
import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.constituency import Constituency
    from app.models.voting_record import VotingRecord


class PollingBooth(Base):
    __tablename__ = "polling_booths"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    booth_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    constituency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("constituencies.id", ondelete="RESTRICT"),
        nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), default="CLOSED", nullable=False)

    constituency: Mapped["Constituency"] = relationship("Constituency", back_populates="polling_booths")
    voting_records: Mapped[list["VotingRecord"]] = relationship("VotingRecord", back_populates="booth",foreign_keys="VotingRecord.polling_booth_id")
