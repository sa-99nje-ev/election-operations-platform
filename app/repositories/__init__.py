"""
Data access layer (Repository pattern).

This package contains repository classes that provide data access operations
for all entity types in the application. Each repository inherits from
BaseRepository and provides entity-specific queries and operations.
"""

from .base import BaseRepository
from .user_repository import UserRepository
from .voter_repository import VoterRepository
from .candidate_repository import CandidateRepository
from .constituency_repository import ConstituencyRepository
from .polling_booth_repository import PollingBoothRepository
from .voting_record_repository import VotingRecordRepository
from .refresh_token_repository import RefreshTokenRepository
from .audit_log_repository import AuditLogRepository

__all__ = [
    'BaseRepository',
    'UserRepository',
    'VoterRepository',
    'CandidateRepository',
    'ConstituencyRepository',
    'PollingBoothRepository',
    'VotingRecordRepository',
    'RefreshTokenRepository',
    'AuditLogRepository',
]
