"""
Constituency management service for administrative setup and district queries.
"""

import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.constituency import Constituency
from app.repositories.constituency_repository import ConstituencyRepository
from app.utils.exceptions import ConstituencyNotFoundError, DuplicateConstituencyError, DatabaseError


class ConstituencyService:
    """Business service for managing electoral districts/constituencies."""

    def __init__(self, session: Session, constituency_repo: ConstituencyRepository):
        self.session = session
        self.constituency_repo = constituency_repo

    def create_constituency(self, name: str, region: str) -> Constituency:
        """Create a new constituency checking for duplicate names."""
        if self.constituency_repo.name_exists(name):
            raise DuplicateConstituencyError(
                f"Constituency with name '{name}' already exists",
                {'name': name}
            )

        try:
            constituency = Constituency(name=name, region=region)
            result = self.constituency_repo.create(constituency)
            self.session.commit()
            return result
        except SQLAlchemyError as e:
            self.session.rollback()
            raise DatabaseError("Failed to create constituency", {'error': str(e)})

    def get_constituency_by_id(self, constituency_id: uuid.UUID) -> Optional[Constituency]:
        """Retrieve constituency by ID."""
        return self.constituency_repo.get_by_id(constituency_id)

    def get_constituency_by_name(self, name: str) -> Optional[Constituency]:
        """Retrieve constituency by name."""
        return self.constituency_repo.get_by_name(name)

    def get_all_constituencies(self, skip: int = 0, limit: int = 100) -> List[Constituency]:
        """Get list of all constituencies."""
        return self.constituency_repo.get_all(skip=skip, limit=limit)

    def count_all_constituencies(self) -> int:
        """Get total count of constituencies."""
        return self.constituency_repo.count_all()

    def update_constituency(self, constituency_id: uuid.UUID, updates: Dict[str, Any]) -> Constituency:
        """Update constituency details."""
        constituency = self.constituency_repo.get_by_id(constituency_id)
        if not constituency:
            raise ConstituencyNotFoundError(f"Constituency '{constituency_id}' not found")

        if 'name' in updates:
            # Check for duplicate name if changing
            if updates['name'] != constituency.name:
                if self.constituency_repo.name_exists(updates['name']):
                    raise DuplicateConstituencyError(
                        f"Constituency with name '{updates['name']}' already exists",
                        {'name': updates['name']}
                    )
            constituency.name = updates['name']
        
        if 'region' in updates:
            constituency.region = updates['region']

        try:
            self.constituency_repo.update(constituency)
            self.session.commit()
            return constituency
        except SQLAlchemyError as e:
            self.session.rollback()
            raise DatabaseError("Failed to update constituency", {'error': str(e)})

    def delete_constituency(self, constituency_id: uuid.UUID) -> bool:
        """Delete a constituency."""
        try:
            result = self.constituency_repo.delete(constituency_id)
            self.session.commit()
            return result
        except SQLAlchemyError as e:
            self.session.rollback()
            raise DatabaseError("Failed to delete constituency", {'error': str(e)})

    def get_constituency_stats(self, constituency_id: uuid.UUID) -> Dict[str, Any]:
        """Get analytical statistics for a specified constituency."""
        return self.constituency_repo.get_constituency_stats(constituency_id)