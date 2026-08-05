"""
Enums and constants for the Election Operations Platform.
"""
from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, Any


class UserRole(str, Enum):
    """User roles with permissions."""
    ADMIN = "Admin"
    ELECTION_OFFICER = "Election_Officer"
    POLLING_OFFICER = "Polling_Officer"
    CANDIDATE = "Candidate"
    VOTER = "Voter"


class VoterStatus(str, Enum):
    """Voter account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class BoothStatus(str, Enum):
    """Polling booth operational status."""
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class AuditOutcome(str, Enum):
    """Audit log event outcomes."""
    SUCCESS = "success"
    FAILURE = "failure"
    VALIDATED = "validated"


class AuditEventType(str, Enum):
    """Audit log event types."""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    VOTE_SUBMISSION = "vote_submission"
    VOTE_COMPLETED = "vote_completed"
    VOTE_FAILED = "vote_failed"
    BOOTH_STATUS_CHANGE = "booth_status_change"
    VOTER_REGISTERED = "voter_registered"
    VOTER_UPDATED = "voter_updated"
    CANDIDATE_REGISTERED = "candidate_registered"
    CANDIDATE_UPDATED = "candidate_updated"
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DEACTIVATED = "user_deactivated"
    USER_ACTIVATED = "user_activated"


@dataclass(frozen=True)
class ElectionConfig:
    """Configuration constants for election operations."""
    
    # Candidate limits
    MAX_CANDIDATES_PER_CONSTITUENCY: int = 20
    
    # Booth capacity limits
    MIN_BOOTH_CAPACITY: int = 1
    MAX_BOOTH_CAPACITY: int = 10000
    
    # Password requirements
    MIN_PASSWORD_LENGTH: int = 8
    MAX_PASSWORD_LENGTH: int = 128
    REQUIRE_SPECIAL_CHAR: bool = True
    REQUIRE_DIGIT: bool = True
    REQUIRE_UPPERCASE: bool = True
    REQUIRE_LOWERCASE: bool = True
    
    # Audit retention
    AUDIT_RETENTION_DAYS: int = 365
    
    # Token expiry (seconds)
    ACCESS_TOKEN_EXPIRY: int = 900  # 15 minutes
    REFRESH_TOKEN_EXPIRY: int = 604800  # 7 days
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'MAX_CANDIDATES_PER_CONSTITUENCY': self.MAX_CANDIDATES_PER_CONSTITUENCY,
            'MIN_BOOTH_CAPACITY': self.MIN_BOOTH_CAPACITY,
            'MAX_BOOTH_CAPACITY': self.MAX_BOOTH_CAPACITY,
            'MIN_PASSWORD_LENGTH': self.MIN_PASSWORD_LENGTH,
            'MAX_PASSWORD_LENGTH': self.MAX_PASSWORD_LENGTH,
            'REQUIRE_SPECIAL_CHAR': self.REQUIRE_SPECIAL_CHAR,
            'REQUIRE_DIGIT': self.REQUIRE_DIGIT,
            'REQUIRE_UPPERCASE': self.REQUIRE_UPPERCASE,
            'REQUIRE_LOWERCASE': self.REQUIRE_LOWERCASE,
            'ACCESS_TOKEN_EXPIRY': self.ACCESS_TOKEN_EXPIRY,
            'REFRESH_TOKEN_EXPIRY': self.REFRESH_TOKEN_EXPIRY,
        }


# Default configuration instance
CONFIG = ElectionConfig()


class PasswordPolicy:
    """Password policy validator using configuration."""
    
    @classmethod
    def validate(cls, password: str) -> None:
        """Validate password against configured policy."""
        from app.utils.exceptions import InvalidPasswordError
        
        if len(password) < CONFIG.MIN_PASSWORD_LENGTH:
            raise InvalidPasswordError(
                f"Password must be at least {CONFIG.MIN_PASSWORD_LENGTH} characters"
            )
        
        if len(password) > CONFIG.MAX_PASSWORD_LENGTH:
            raise InvalidPasswordError(
                f"Password must be at most {CONFIG.MAX_PASSWORD_LENGTH} characters"
            )
        
        if CONFIG.REQUIRE_DIGIT and not any(c.isdigit() for c in password):
            raise InvalidPasswordError("Password must contain at least one digit")
        
        if CONFIG.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            raise InvalidPasswordError("Password must contain at least one uppercase letter")
        
        if CONFIG.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            raise InvalidPasswordError("Password must contain at least one lowercase letter")
        
        if CONFIG.REQUIRE_SPECIAL_CHAR and not any(c in "!@#$%^&*(),.?\":{}|<>" for c in password):
            raise InvalidPasswordError("Password must contain at least one special character")