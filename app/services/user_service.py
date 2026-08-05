"""
User management service for creating, updating, and managing user accounts.
"""

import uuid
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.utils.password import hash_and_encode_password, validate_password_strength


class UserService:
    """Business service for user account management."""

    def __init__(self, session: Session, user_repo: UserRepository):
        self.session = session
        self.user_repo = user_repo

    def create_user(self, username: str, password: str, role: str) -> User:
        """Create a new user account with hashed password."""
        if self.user_repo.get_by_username(username):
            raise ValueError(f"Username '{username}' already exists")

        validate_password_strength(password)
        password_hash = hash_and_encode_password(password)

        user = User(
            username=username,
            password_hash=password_hash,
            role=role
        )
        return self.user_repo.create(user)

    def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Retrieve user by ID."""
        return self.user_repo.get_by_id(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Retrieve user by username."""
        return self.user_repo.get_by_username(username)

    def get_all_users(self) -> List[User]:
        """Get all users."""
        return self.user_repo.get_all()

    def update_user_role(self, user_id: uuid.UUID, role: str) -> bool:
        """Update a user's role."""
        return self.user_repo.update_role(user_id, role)

    def deactivate_user(self, user_id: uuid.UUID) -> bool:
        """Deactivate a user account."""
        return self.user_repo.deactivate_user(user_id)

    def activate_user(self, user_id: uuid.UUID) -> bool:
        """Activate a user account."""
        return self.user_repo.activate_user(user_id)
