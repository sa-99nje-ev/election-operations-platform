"""
Refresh token repository for database operations on RefreshToken entities.

This module implements the RefreshTokenRepository class that provides specialized
database operations for RefreshToken entities for token management and revocation.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
import uuid
from datetime import datetime

from app.models.refresh_token import RefreshToken
from .base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    """
    Repository for RefreshToken entity operations.
    
    Provides specialized queries and operations for RefreshToken entities beyond
    the generic CRUD operations from BaseRepository.
    """
    
    def __init__(self, session: Session):
        """
        Initialize RefreshTokenRepository with RefreshToken model class.
        
        Args:
            session: SQLAlchemy database session
        """
        super().__init__(RefreshToken, session)
    
    def get_by_token_hash(self, token_hash: str) -> Optional[RefreshToken]:
        """
        Retrieve a refresh token by token hash.
        
        Args:
            token_hash: Refresh token hash to search for
            
        Returns:
            RefreshToken entity if found, None otherwise
        """
        return self.session.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash
        ).first()
    
    def get_by_user(self, user_id: uuid.UUID) -> List[RefreshToken]:
        """
        Retrieve all refresh tokens for a specific user.
        
        Args:
            user_id: User ID to filter by
            
        Returns:
            List of refresh tokens for the specified user
        """
        return self.session.query(RefreshToken).filter(
            RefreshToken.user_id == user_id
        ).all()
    
    def get_active_by_user(self, user_id: uuid.UUID) -> List[RefreshToken]:
        """
        Retrieve active refresh tokens for a specific user.
        
        Args:
            user_id: User ID to filter by
            
        Returns:
            List of active (not invalidated and not expired) refresh tokens for the user
        """
        now = datetime.utcnow()
        return self.session.query(RefreshToken).filter(
            and_(
                RefreshToken.user_id == user_id,
                RefreshToken.invalidated == False,
                RefreshToken.expires_at > now
            )
        ).all()
    
    def token_hash_exists(self, token_hash: str) -> bool:
        """
        Check if a refresh token hash already exists.
        
        Args:
            token_hash: Refresh token hash to check
            
        Returns:
            True if token hash exists, False otherwise
        """
        return self.get_by_token_hash(token_hash) is not None
    
    def is_token_valid(self, token_hash: str) -> bool:
        """
        Check if a refresh token is valid (not invalidated and not expired).
        
        Args:
            token_hash: Refresh token hash to check
            
        Returns:
            True if token is valid, False otherwise
        """
        refresh_token = self.get_by_token_hash(token_hash)
        if refresh_token is None:
            return False
        
        now = datetime.utcnow()
        return (
            not refresh_token.invalidated and
            refresh_token.expires_at > now
        )
    
    def invalidate_token(self, token_hash: str) -> bool:
        """
        Invalidate a refresh token by setting invalidated flag.
        
        Args:
            token_hash: Refresh token hash to invalidate
            
        Returns:
            True if token was invalidated, False if token not found or already invalidated
        """
        refresh_token = self.get_by_token_hash(token_hash)
        if refresh_token is None:
            return False
        
        # Check if token is already invalidated
        if refresh_token.invalidated:
            return True
        
        refresh_token.invalidated = True
        self.session.flush()
        return True
    
    def invalidate_all_user_tokens(self, user_id: uuid.UUID) -> int:
        """
        Invalidate all refresh tokens for a specific user.
        
        Args:
            user_id: User ID to invalidate tokens for
            
        Returns:
            Number of tokens invalidated
        """
        tokens = self.session.query(RefreshToken).filter(
            and_(
                RefreshToken.user_id == user_id,
                RefreshToken.invalidated == False
            )
        ).all()
        
        invalidated_count = 0
        for token in tokens:
            token.invalidated = True
            invalidated_count += 1
        
        if invalidated_count > 0:
            self.session.flush()
        
        return invalidated_count
    
    def invalidate_token_by_id(self, token_id: uuid.UUID) -> bool:
        """
        Invalidate a refresh token by its ID.
        
        Args:
            token_id: Refresh token ID to invalidate
            
        Returns:
            True if token was invalidated, False if token not found or already invalidated
        """
        refresh_token = self.get_by_id(token_id)
        if refresh_token is None:
            return False
        
        # Check if token is already invalidated
        if refresh_token.invalidated:
            return True
        
        refresh_token.invalidated = True
        self.session.flush()
        return True
    
    def cleanup_expired_tokens(self) -> int:
        """
        Delete expired refresh tokens from the database.
        
        Returns:
            Number of tokens deleted
        """
        now = datetime.utcnow()
        
        # Find expired tokens
        expired_tokens = self.session.query(RefreshToken).filter(
            RefreshToken.expires_at <= now
        ).all()
        
        deleted_count = 0
        for token in expired_tokens:
            self.session.delete(token)
            deleted_count += 1
        
        if deleted_count > 0:
            self.session.flush()
        
        return deleted_count
    
    def create_token(
        self,
        user_id: uuid.UUID,
        token_hash: str,
        expires_at: datetime
    ) -> RefreshToken:
        """
        Create a new refresh token.
        
        Args:
            user_id: User ID associated with the token
            token_hash: Hashed refresh token value
            expires_at: Token expiration datetime
            
        Returns:
            Created RefreshToken entity
            
        Raises:
            ValueError: If token hash already exists
        """
        # Check if token hash already exists
        if self.token_hash_exists(token_hash):
            raise ValueError(f"Token hash already exists")
        
        # Create new refresh token
        refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            invalidated=False
        )
        
        self.session.add(refresh_token)
        self.session.flush()
        
        return refresh_token
    
    def get_token_with_user(self, token_hash: str) -> Optional[RefreshToken]:
        """
        Retrieve a refresh token with its associated user eagerly loaded.
        
        Args:
            token_hash: Refresh token hash to retrieve
            
        Returns:
            RefreshToken entity with user if found, None otherwise
        """
        from sqlalchemy.orm import joinedload
        
        return self.session.query(RefreshToken).options(
            joinedload(RefreshToken.user)
        ).filter(RefreshToken.token_hash == token_hash).first()
    
    def get_token_stats(self) -> dict:
        """
        Get refresh token statistics.
        
        Returns:
            Dictionary with token statistics
        """
        from sqlalchemy import func
        
        # Total tokens
        total_tokens = self.session.query(RefreshToken).count()
        
        # Active tokens (not invalidated and not expired)
        now = datetime.utcnow()
        active_tokens = self.session.query(RefreshToken).filter(
            and_(
                RefreshToken.invalidated == False,
                RefreshToken.expires_at > now
            )
        ).count()
        
        # Invalidated tokens
        invalidated_tokens = self.session.query(RefreshToken).filter(
            RefreshToken.invalidated == True
        ).count()
        
        # Expired tokens
        expired_tokens = self.session.query(RefreshToken).filter(
            and_(
                RefreshToken.invalidated == False,
                RefreshToken.expires_at <= now
            )
        ).count()
        
        # Tokens by user
        tokens_by_user = self.session.query(
            RefreshToken.user_id,
            func.count(RefreshToken.id).label('token_count')
        ).group_by(RefreshToken.user_id).all()
        
        return {
            'total_tokens': total_tokens,
            'active_tokens': active_tokens,
            'invalidated_tokens': invalidated_tokens,
            'expired_tokens': expired_tokens,
            'tokens_by_user': [
                {'user_id': str(user_id), 'token_count': token_count}
                for user_id, token_count in tokens_by_user
            ]
        }
    
    def get_recent_tokens(self, limit: int = 100) -> List[RefreshToken]:
        """
        Retrieve recently created refresh tokens.
        
        Args:
            limit: Maximum number of tokens to return
            
        Returns:
            List of recent refresh tokens
        """
        return self.session.query(RefreshToken).order_by(
            RefreshToken.created_at.desc()
        ).limit(limit).all()