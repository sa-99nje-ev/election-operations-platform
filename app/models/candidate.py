from __future__ import annotations
import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.constituency import Constituency
    from app.models.user import User
    from app.models.voting_record import VotingRecord


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    national_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    party: Mapped[str] = mapped_column(String(100), nullable=False)
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

    constituency: Mapped["Constituency"] = relationship("Constituency", foreign_keys=[constituency_id])
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    voting_records: Mapped[list["VotingRecord"]] = relationship("VotingRecord", back_populates="candidate")
