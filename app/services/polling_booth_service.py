"""
Polling booth management service handling booth code validation, capacity, and status changes.
"""

import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app.models.polling_booth import PollingBooth
from app.repositories.polling_booth_repository import PollingBoothRepository
from app.repositories.constituency_repository import ConstituencyRepository
from app.utils.enums import CONFIG, BoothStatus
from app.utils.exceptions import (
    DuplicateBoothError,
    ConstituencyNotFoundError,
    BoothNotFoundError,
    BoothAlreadyOpenError,
    BoothAlreadyClosedError,
    BoothCapacityExceededError,
    DatabaseError
)


class PollingBoothService:
    """Business service for physical polling booth operations."""

    def __init__(self, session: Session, booth_repo: PollingBoothRepository, constituency_repo: ConstituencyRepository):
        self.session = session
        self.booth_repo = booth_repo
        self.constituency_repo = constituency_repo

    def create_polling_booth(
        self,
        booth_code: str,
        location: str,
        capacity: int,
        constituency_id: uuid.UUID
    ) -> PollingBooth:
        """Create a new polling booth ensuring code uniqueness and valid capacity."""
        if self.booth_repo.code_exists(booth_code):
            raise DuplicateBoothError(
                f"Polling booth code '{booth_code}' already exists",
                {'booth_code': booth_code}
            )

        constituency = self.constituency_repo.get_by_id(constituency_id)
        if not constituency:
            raise ConstituencyNotFoundError(
                f"Constituency '{constituency_id}' not found",
                {'constituency_id': str(constituency_id)}
            )

        if capacity < CONFIG.MIN_BOOTH_CAPACITY or capacity > CONFIG.MAX_BOOTH_CAPACITY:
            raise BoothCapacityExceededError(
                f"Booth capacity must be between {CONFIG.MIN_BOOTH_CAPACITY} and {CONFIG.MAX_BOOTH_CAPACITY}",
                {'capacity': capacity, 'min': CONFIG.MIN_BOOTH_CAPACITY, 'max': CONFIG.MAX_BOOTH_CAPACITY}
            )

        try:
            booth = PollingBooth(
                booth_code=booth_code,
                location=location,
                capacity=capacity,
                constituency_id=constituency_id,
                status=BoothStatus.CLOSED.value
            )
            result = self.booth_repo.create(booth)
            self.session.commit()
            return result
        except Exception as e:
            self.session.rollback()
            raise DatabaseError("Failed to create polling booth", {'error': str(e)})

    def get_booth_by_id(self, booth_id: uuid.UUID) -> Optional[PollingBooth]:
        """Retrieve polling booth by ID."""
        return self.booth_repo.get_by_id(booth_id)

    def get_booth_by_code(self, booth_code: str) -> Optional[PollingBooth]:
        """Retrieve polling booth by unique booth code."""
        return self.booth_repo.get_by_code(booth_code)

    def get_all_polling_booths(self, skip: int = 0, limit: int = 100) -> List[PollingBooth]:
        """Get all polling booths with pagination."""
        return self.booth_repo.get_all(skip=skip, limit=limit)

    def count_all_polling_booths(self) -> int:
        """Get total count of polling booths."""
        return self.booth_repo.count_all()

    def get_booths_by_constituency(
        self,
        constituency_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[PollingBooth]:
        """Get polling booths in a specified constituency."""
        return self.booth_repo.get_by_constituency(constituency_id, skip=skip, limit=limit)

    def count_booths_by_constituency(self, constituency_id: uuid.UUID) -> int:
        """Get count of polling booths in a constituency."""
        return self.booth_repo.count_by_constituency(constituency_id)

    def open_polling_booth(self, booth_id: uuid.UUID) -> PollingBooth:
        """Set polling booth status to OPEN."""
        booth = self.booth_repo.get_by_id(booth_id)
        if not booth:
            raise BoothNotFoundError(f"Booth '{booth_id}' not found")

        if booth.status == BoothStatus.OPEN.value:
            raise BoothAlreadyOpenError(f"Booth '{booth_id}' is already open")

        try:
            booth.status = BoothStatus.OPEN.value
            self.booth_repo.update(booth)
            self.session.commit()
            return booth
        except Exception as e:
            self.session.rollback()
            raise DatabaseError("Failed to open polling booth", {'error': str(e)})

    def close_polling_booth(self, booth_id: uuid.UUID) -> PollingBooth:
        """Set polling booth status to CLOSED."""
        booth = self.booth_repo.get_by_id(booth_id)
        if not booth:
            raise BoothNotFoundError(f"Booth '{booth_id}' not found")

        if booth.status == BoothStatus.CLOSED.value:
            raise BoothAlreadyClosedError(f"Booth '{booth_id}' is already closed")

        try:
            booth.status = BoothStatus.CLOSED.value
            self.booth_repo.update(booth)
            self.session.commit()
            return booth
        except Exception as e:
            self.session.rollback()
            raise DatabaseError("Failed to close polling booth", {'error': str(e)})

    def update_capacity(self, booth_id: uuid.UUID, capacity: int) -> PollingBooth:
        """Update polling booth capacity limit."""
        booth = self.booth_repo.get_by_id(booth_id)
        if not booth:
            raise BoothNotFoundError(f"Booth '{booth_id}' not found")

        if capacity < CONFIG.MIN_BOOTH_CAPACITY or capacity > CONFIG.MAX_BOOTH_CAPACITY:
            raise BoothCapacityExceededError(
                f"Booth capacity must be between {CONFIG.MIN_BOOTH_CAPACITY} and {CONFIG.MAX_BOOTH_CAPACITY}",
                {'capacity': capacity, 'min': CONFIG.MIN_BOOTH_CAPACITY, 'max': CONFIG.MAX_BOOTH_CAPACITY}
            )

        try:
            booth.capacity = capacity
            self.booth_repo.update(booth)
            self.session.commit()
            return booth
        except Exception as e:
            self.session.rollback()
            raise DatabaseError("Failed to update booth capacity", {'error': str(e)})

    def get_booth_stats(self, booth_id: uuid.UUID) -> Dict[str, Any]:
        """Get polling booth utilization statistics."""
        return self.booth_repo.get_polling_booth_stats(booth_id)