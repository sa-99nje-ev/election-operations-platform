import uuid
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class PollingBooth(Base):
    __tablename__ = "polling_booths"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    booth_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, default=1000)
    constituency_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active")

    # Relationships
    constituency = relationship("Constituency", back_populates="polling_booths")
    voting_records = relationship("VotingRecord", back_populates="booth")