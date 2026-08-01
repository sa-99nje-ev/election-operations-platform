"""
SQLAlchemy ORM models package.

This package contains all database models for the election operations platform.
Models are built using SQLAlchemy 2.0 declarative style with proper relationships,
constraints, and indexes.

Available Models:
    - User: User accounts with role-based access control
    - Constituency: Electoral districts/constituencies
    - Voter: Registered voters
    - Candidate: Election candidates
    - PollingBooth: Physical voting locations
    - VotingRecord: Individual vote records (with duplicate prevention)
    - AuditLog: Security and compliance audit trail
    - RefreshToken: JWT refresh token storage
"""

from app.models.user import User
from app.models.constituency import Constituency
from app.models.voter import Voter
from app.models.candidate import Candidate
from app.models.polling_booth import PollingBooth
from app.models.voting_record import VotingRecord
from app.models.audit_log import AuditLog
from app.models.refresh_token import RefreshToken

__all__ = [
    'User',
    'Constituency',
    'Voter',
    'Candidate',
    'PollingBooth',
    'VotingRecord',
    'AuditLog',
    'RefreshToken',
]
