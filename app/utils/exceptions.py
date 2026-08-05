"""
Custom exceptions for the Election Operations Platform.
All domain-specific exceptions inherit from ElectionException.
"""

from typing import Optional, Any


class ElectionException(Exception):
    """Base exception for all election platform errors."""
    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class AuthenticationError(ElectionException):
    """Raised when authentication fails."""
    pass


class AuthorizationError(ElectionException):
    """Raised when user lacks required permissions."""
    pass


class DuplicateVoteError(ElectionException):
    """Raised when a voter attempts to vote more than once."""
    pass


class DuplicateVoterError(ElectionException):
    """Raised when a voter with the same national ID is already registered."""
    pass


class DuplicateCandidateError(ElectionException):
    """Raised when a candidate with the same national ID is already registered."""
    pass


class DuplicateUserError(ElectionException):
    """Raised when a user with the same username already exists."""
    pass


class DuplicateConstituencyError(ElectionException):
    """Raised when a constituency with the same name already exists."""
    pass


class DuplicateBoothError(ElectionException):
    """Raised when a booth with the same code already exists."""
    pass


class CandidateNotFoundError(ElectionException):
    """Raised when a candidate does not exist."""
    pass


class VoterNotFoundError(ElectionException):
    """Raised when a voter does not exist."""
    pass


class UserNotFoundError(ElectionException):
    """Raised when a user does not exist."""
    pass


class BoothNotFoundError(ElectionException):
    """Raised when a polling booth does not exist."""
    pass


class BoothClosedError(ElectionException):
    """Raised when a polling booth is closed."""
    pass


class BoothAlreadyOpenError(ElectionException):
    """Raised when attempting to open an already open booth."""
    pass


class BoothAlreadyClosedError(ElectionException):
    """Raised when attempting to close an already closed booth."""
    pass


class BoothCapacityExceededError(ElectionException):
    """Raised when booth capacity is exceeded."""
    pass


class ConstituencyNotFoundError(ElectionException):
    """Raised when a constituency does not exist."""
    pass


class InvalidConstituencyError(ElectionException):
    """Raised when a constituency is invalid or mismatched."""
    pass


class CandidateNotInConstituencyError(ElectionException):
    """Raised when a candidate is not registered in the voter's constituency."""
    pass


class MaxCandidatesReachedError(ElectionException):
    """Raised when a constituency has reached the maximum candidate limit."""
    pass


class RefreshTokenInvalidError(ElectionException):
    """Raised when a refresh token is invalid or expired."""
    pass


class AuditLogError(ElectionException):
    """Raised when audit logging fails."""
    pass


class InvalidPasswordError(ElectionException):
    """Raised when a password fails validation."""
    pass


class DatabaseError(ElectionException):
    """Raised for database-related errors."""
    pass


class QueueError(ElectionException):
    """Raised for queue-related errors."""
    pass


class ValidationError(ElectionException):
    """Raised for validation errors."""
    pass


class ResourceNotFoundError(ElectionException):
    """Raised when a resource is not found."""
    pass


class BusinessRuleViolationError(ElectionException):
    """Raised when a business rule is violated."""
    pass


class InvalidNationalIdError(ElectionException):
    """Raised when a national ID is invalid."""
    pass


class InvalidDateError(ElectionException):
    """Raised when a date is invalid."""
    pass


class ElectionNotActiveError(ElectionException):
    """Raised when an operation is attempted outside the election window."""
    pass