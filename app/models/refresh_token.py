"""
Refresh token model for JWT token management.

This model stores hashed refresh tokens for user sessions. Refresh tokens allow
users to obtain new access tokens without re-authenticating. Tokens can be
invalidated for logout/security purposes and automatically expire.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class RefreshToken(Base):
    """
    JWT refresh token model for session management.
    
    Attributes:
        id: Unique token identifier (UUID v4)
        user_id: Foreign key to users table (token owner)
        token_hash: Hashed token value (UNIQUE, max 255 chars)
        expires_at: Token expiration timestamp (timezone-aware)
        invalidated: Token invalidation flag (for logout/revocation)
    
    Relationships:
        user: Many-to-one with User (token owner)
    
    Security Notes:
        - Tokens are stored as hashes, never in plain text
        - Expired tokens should be periodically purged
        - Invalidated tokens cannot be used even if not expired
    """
    
    __tablename__ = 'refresh_tokens'
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    
    # Foreign key
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='RESTRICT'),
        nullable=False,
        index=True
    )
    
    # Token hash (unique)
    token_hash: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    
    # Expiration timestamp
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    
    # Invalidation flag
    invalidated: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default='false'
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="refresh_tokens"
    )
    
    def __repr__(self) -> str:
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, expires_at={self.expires_at}, invalidated={self.invalidated})>"
