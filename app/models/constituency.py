from __future__ import annotations
import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.voter import Voter
    from app.models.candidate import Candidate
    from app.models.polling_booth import PollingBooth


class Constituency(Base):
    __tablename__ = "constituencies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    region: Mapped[str] = mapped_column(String(100), nullable=False)

    voters: Mapped[list["Voter"]] = relationship("Voter", back_populates="constituency")
    candidates: Mapped[list["Candidate"]] = relationship("Candidate", back_populates="constituency")
    polling_booths: Mapped[list["PollingBooth"]] = relationship("PollingBooth", back_populates="constituency")
