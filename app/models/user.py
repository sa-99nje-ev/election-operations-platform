"""
User model for authentication and authorization.

This model stores user account information including credentials and role-based
access control. Each user has exactly one role (Admin, Election_Officer, etc.)
and may be associated with a Voter or Candidate profile.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.extensions import db


class User(db.Model):
    """
    User account model with role-based access control.
    
    Attributes:
        id: Unique user identifier (UUID v4)
        username: Unique login username (max 50 chars)
        password_hash: Bcrypt password hash (cost factor 12)
        role: User role (Admin, Election_Officer, Polling_Officer, Candidate, Voter)
        created_at: Account creation timestamp (timezone-aware)
    
    Relationships:
        voters: One-to-many with Voter (one user may have one voter profile)
        candidates: One-to-many with Candidate (one user may have one candidate profile)
        audit_logs: One-to-many with AuditLog (actions performed by this user)
        refresh_tokens: One-to-many with RefreshToken (active sessions)
    """
    
    __tablename__ = 'users'
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    
    # Unique username for login
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    
    # Bcrypt password hash
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    # Role-based access control
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    
    # Relationships
    voters: Mapped[list["Voter"]] = relationship(
        "Voter",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    candidates: Mapped[list["Candidate"]] = relationship(
        "Candidate",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="actor",
        cascade="all, delete-orphan"
    )
    
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"
