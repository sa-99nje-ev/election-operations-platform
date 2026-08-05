import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class VotingRecord(Base):
    __tablename__ = "voting_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    voter_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("voters.id"), nullable=False)
    candidate_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    polling_booth_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("polling_booths.id"), nullable=False)
    transaction_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    voter = relationship("Voter", back_populates="voting_records")
    candidate = relationship("Candidate", back_populates="voting_records")
    booth = relationship("PollingBooth", back_populates="voting_records")