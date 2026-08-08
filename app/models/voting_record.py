from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.voter import Voter
    from app.models.candidate import Candidate
    from app.models.polling_booth import PollingBooth


class VotingRecord(Base):
    __tablename__ = "voting_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=True
    )
    voter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("voters.id", ondelete="RESTRICT"),
        nullable=False
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("candidates.id", ondelete="RESTRICT"),
        nullable=False
    )
    booth_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("polling_booths.id", ondelete="RESTRICT"),
        nullable=True
    )
    polling_booth_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("polling_booths.id"),
        nullable=True
    )
    transaction_id: Mapped[str] = mapped_column(String(64), nullable=True)
    voted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    voter: Mapped["Voter"] = relationship("Voter", back_populates="voting_records")
    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="voting_records")
    booth: Mapped["PollingBooth"] = relationship("PollingBooth", back_populates="voting_records",foreign_keys=[polling_booth_id])