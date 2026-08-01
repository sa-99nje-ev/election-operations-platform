"""
User repository for database operations on User entities.

This module implements the UserRepository class that provides specialized
database operations for User entities beyond the generic CRUD operations
provided by BaseRepository.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
import uuid

from app.models.user import User
from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Repository for User entity operations.
    
    Provides specialized queries and operations for User entities beyond
    the generic CRUD operations from BaseRepository.
    """
    
    def __init__(self, session: Session):
        """
        Initialize UserRepository with User model class.
        
        Args:
            session: SQLAlchemy database session
        """
        super().__init__(User, session)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Retrieve a user by username (case-insensitive).
        
        Args:
            username: Username to search for
            
        Returns:
            User entity if found, None otherwise
        """
        return self.session.query(User).filter(
            User.username.ilike(username)
        ).first()
    
    def get_by_role(self, role: str) -> List[User]:
        """
        Retrieve all users with a specific role.
        
        Args:
            role: User role to filter by
            
        Returns:
            List of users with the specified role
        """
        return self.session.query(User).filter(
            User.role == role
        ).all()
    
    def search_users(self, search_term: str) -> List[User]:
        """
        Search users by username (partial match, case-insensitive).
        
        Args:
            search_term: Search term to match against usernames
            
        Returns:
            List of users matching the search term
        """
        return self.session.query(User).filter(
            User.username.ilike(f'%{search_term}%')
        ).all()
    
    def get_active_users(self) -> List[User]:
        """
        Retrieve all active users (users without deleted_at timestamp).
        
        Returns:
            List of active users
        """
        return self.session.query(User).filter(
            User.deleted_at.is_(None)
        ).all()
    
    def get_users_by_roles(self, roles: List[str]) -> List[User]:
        """
        Retrieve users with any of the specified roles.
        
        Args:
            roles: List of roles to filter by
            
        Returns:
            List of users with any of the specified roles
        """
        if not roles:
            return []
        
        return self.session.query(User).filter(
            User.role.in_(roles)
        ).all()
    
    def username_exists(self, username: str, exclude_user_id: Optional[uuid.UUID] = None) -> bool:
        """
        Check if a username already exists (case-insensitive).
        
        Args:
            username: Username to check
            exclude_user_id: Optional user ID to exclude from check
                           (useful when updating a user's own username)
            
        Returns:
            True if username exists, False otherwise
        """
        query = self.session.query(User).filter(
            User.username.ilike(username)
        )
        
        if exclude_user_id:
            query = query.filter(User.id != exclude_user_id)
        
        return query.first() is not None
    
    def update_password(self, user_id: uuid.UUID, password_hash: str) -> bool:
        """
        Update a user's password hash.
        
        Args:
            user_id: User ID to update
            password_hash: New bcrypt password hash
            
        Returns:
            True if password was updated, False if user not found
            
        Raises:
            ValueError: If password_hash is empty or invalid
        """
        if not password_hash:
            raise ValueError("Password hash cannot be empty")
        
        user = self.get_by_id(user_id)
        if user is None:
            return False
        
        user.password_hash = password_hash
        self.session.flush()
        return True
    
    def deactivate_user(self, user_id: uuid.UUID) -> bool:
        """
        Deactivate a user by setting deleted_at timestamp.
        
        Args:
            user_id: User ID to deactivate
            
        Returns:
            True if user was deactivated, False if user not found
        """
        user = self.get_by_id(user_id)
        if user is None:
            return False
        
        # Check if user is already deactivated
        if user.deleted_at is not None:
            return True
        
        # Import here to avoid circular import
        from datetime import datetime
        user.deleted_at = datetime.utcnow()
        self.session.flush()
        return True
    
    def activate_user(self, user_id: uuid.UUID) -> bool:
        """
        Activate a previously deactivated user by clearing deleted_at.
        
        Args:
            user_id: User ID to activate
            
        Returns:
            True if user was activated, False if user not found
        """
        user = self.get_by_id(user_id)
        if user is None:
            return False
        
        # Check if user is already active
        if user.deleted_at is None:
            return True
        
        user.deleted_at = None
        self.session.flush()
        return True
    
    def get_user_with_voter_profile(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Retrieve a user with their voter profile eagerly loaded.
        
        Args:
            user_id: User ID to retrieve
            
        Returns:
            User entity with voter profile if found, None otherwise
        """
        from sqlalchemy.orm import joinedload
        
        return self.session.query(User).options(
            joinedload(User.voters)
        ).filter(User.id == user_id).first()
    
    def get_user_with_candidate_profile(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Retrieve a user with their candidate profile eagerly loaded.
        
        Args:
            user_id: User ID to retrieve
            
        Returns:
            User entity with candidate profile if found, None otherwise
        """
        from sqlalchemy.orm import joinedload
        
        return self.session.query(User).options(
            joinedload(User.candidates)
        ).filter(User.id == user_id).first()