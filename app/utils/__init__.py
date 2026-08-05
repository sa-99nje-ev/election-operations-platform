"""
Utility modules for common application functionality.
"""

from .password import (
    hash_password,
    verify_password,
    is_password_strong,
    validate_password_strength,
    needs_rehash,
    PasswordError,
    PasswordTooWeakError,
    PasswordVerificationError,
)

from .security import (
    verify_password as verify_security_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)

from .enums import (
    UserRole,
    VoterStatus,
    BoothStatus,
    AuditOutcome,
    AuditEventType,
    ElectionConfig,
    CONFIG,
    PasswordPolicy,
)

from .exceptions import (
    ElectionException,
    AuthenticationError,
    AuthorizationError,
    DuplicateVoteError,
    DuplicateVoterError,
    DuplicateCandidateError,
    DuplicateUserError,
    DuplicateConstituencyError,
    DuplicateBoothError,
    CandidateNotFoundError,
    VoterNotFoundError,
    UserNotFoundError,
    BoothNotFoundError,
    BoothClosedError,
    BoothAlreadyOpenError,
    BoothAlreadyClosedError,
    BoothCapacityExceededError,
    ConstituencyNotFoundError,
    InvalidConstituencyError,
    CandidateNotInConstituencyError,
    MaxCandidatesReachedError,
    RefreshTokenInvalidError,
    AuditLogError,
    InvalidPasswordError,
    DatabaseError,
    QueueError,
    ValidationError,
    ResourceNotFoundError,
    BusinessRuleViolationError,
    InvalidNationalIdError,
    InvalidDateError,
    ElectionNotActiveError,
)

from .logging_config import configure_logging, get_request_id, get_logger

__all__ = [
    # Password utilities
    'hash_password',
    'verify_password',
    'is_password_strong',
    'validate_password_strength',
    'needs_rehash',
    'PasswordError',
    'PasswordTooWeakError',
    'PasswordVerificationError',

    # Security & Tokens
    'verify_security_password',
    'get_password_hash',
    'create_access_token',
    'create_refresh_token',
    'decode_token',

    # Enums and Config
    'UserRole',
    'VoterStatus',
    'BoothStatus',
    'AuditOutcome',
    'AuditEventType',
    'ElectionConfig',
    'CONFIG',
    'PasswordPolicy',

    # Custom Exceptions
    'ElectionException',
    'AuthenticationError',
    'AuthorizationError',
    'DuplicateVoteError',
    'DuplicateVoterError',
    'DuplicateCandidateError',
    'DuplicateUserError',
    'DuplicateConstituencyError',
    'DuplicateBoothError',
    'CandidateNotFoundError',
    'VoterNotFoundError',
    'UserNotFoundError',
    'BoothNotFoundError',
    'BoothClosedError',
    'BoothAlreadyOpenError',
    'BoothAlreadyClosedError',
    'BoothCapacityExceededError',
    'ConstituencyNotFoundError',
    'InvalidConstituencyError',
    'CandidateNotInConstituencyError',
    'MaxCandidatesReachedError',
    'RefreshTokenInvalidError',
    'AuditLogError',
    'InvalidPasswordError',
    'DatabaseError',
    'QueueError',
    'ValidationError',
    'ResourceNotFoundError',
    'BusinessRuleViolationError',
    'InvalidNationalIdError',
    'InvalidDateError',
    'ElectionNotActiveError',

    # Logging
    'configure_logging',
    'get_request_id',
    'get_logger',
]