"""
Password hashing utilities for secure credential storage.

This module provides functions for hashing and verifying passwords using bcrypt
with configurable cost factor. Includes validation rules for password strength.
"""

import bcrypt
import re
from typing import Tuple, Optional
from datetime import datetime

# Password validation constants
MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 128
PASSWORD_COMPLEXITY_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]).+$')

# Bcrypt configuration
BCRYPT_ROUNDS = 12  # Cost factor (recommended minimum for modern systems)
BCRYPT_PREFIX = b'2b'  # Use bcrypt version 2b


class PasswordError(Exception):
    """Base exception for password-related errors."""
    pass


class PasswordTooWeakError(PasswordError):
    """Raised when a password doesn't meet complexity requirements."""
    pass


class PasswordVerificationError(PasswordError):
    """Raised when password verification fails."""
    pass


def hash_password(password: str) -> bytes:
    """
    Hash a password using bcrypt with configured cost factor.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        bytes: Bcrypt hash suitable for storage
        
    Raises:
        PasswordTooWeakError: If password doesn't meet complexity requirements
        ValueError: If password is empty or too long
    """
    if not password:
        raise ValueError("Password cannot be empty")
    
    if len(password) > MAX_PASSWORD_LENGTH:
        raise ValueError(f"Password exceeds maximum length of {MAX_PASSWORD_LENGTH} characters")
    
    # Validate password complexity
    if not is_password_strong(password):
        raise PasswordTooWeakError(
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters and include "
            f"uppercase, lowercase, digits, and special characters"
        )
    
    # Convert password to bytes
    password_bytes = password.encode('utf-8')
    
    # Generate salt and hash
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS, prefix=BCRYPT_PREFIX)
    password_hash = bcrypt.hashpw(password_bytes, salt)
    
    return password_hash


def verify_password(password: str, password_hash: bytes) -> bool:
    """
    Verify a password against a stored hash.
    
    Args:
        password: Plain text password to verify
        password_hash: Bcrypt hash to verify against
        
    Returns:
        bool: True if password matches hash, False otherwise
        
    Raises:
        ValueError: If password is empty or hash is invalid
    """
    if not password:
        raise ValueError("Password cannot be empty")
    
    if not password_hash:
        raise ValueError("Password hash cannot be empty")
    
    # Convert password to bytes
    password_bytes = password.encode('utf-8')
    
    # Verify password
    try:
        return bcrypt.checkpw(password_bytes, password_hash)
    except (ValueError, TypeError) as e:
        raise PasswordVerificationError(f"Password verification failed: {e}")


def is_password_strong(password: str) -> Tuple[bool, Optional[str]]:
    """
    Check if a password meets complexity requirements.
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    # Check length
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters"
    
    if len(password) > MAX_PASSWORD_LENGTH:
        return False, f"Password cannot exceed {MAX_PASSWORD_LENGTH} characters"
    
    # Check complexity using regex
    if not PASSWORD_COMPLEXITY_REGEX.match(password):
        return False, "Password must include uppercase, lowercase, digits, and special characters"
    
    return True, None


def validate_password_strength(password: str) -> None:
    """
    Validate password strength and raise appropriate exception.
    
    Args:
        password: Password to validate
        
    Raises:
        PasswordTooWeakError: If password doesn't meet complexity requirements
    """
    is_valid, error_message = is_password_strong(password)
    if not is_valid:
        raise PasswordTooWeakError(error_message)


def needs_rehash(password_hash: bytes) -> bool:
    """
    Check if a password hash needs to be rehashed (e.g., due to updated cost factor).
    
    Args:
        password_hash: Bcrypt hash to check
        
    Returns:
        bool: True if hash should be rehashed, False otherwise
        
    Raises:
        ValueError: If hash is invalid
    """
    if not password_hash:
        raise ValueError("Password hash cannot be empty")
    
    # Extract cost factor from hash
    try:
        # Bcrypt hash format: $2b$12$salt.hash
        parts = password_hash.decode('utf-8').split('$')
        if len(parts) < 4:
            return True
        
        # Get cost factor
        cost_factor = int(parts[2])
        
        # Check if cost factor is below current standard
        return cost_factor < BCRYPT_ROUNDS
        
    except (ValueError, IndexError, UnicodeDecodeError):
        # Invalid hash format, should be rehashed
        return True


# Convenience functions for common operations
def hash_and_encode_password(password: str) -> str:
    """Hash password and encode as UTF-8 string for storage."""
    return hash_password(password).decode('utf-8')


def verify_encoded_password(password: str, encoded_hash: str) -> bool:
    """Verify password against encoded hash string."""
    return verify_password(password, encoded_hash.encode('utf-8'))