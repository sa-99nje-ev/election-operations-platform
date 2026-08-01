"""
JWT token management utilities for authentication and authorization.

This module provides functions for generating, validating, and managing JWT tokens
with support for refresh tokens and token blacklisting.
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt,
    decode_token,
    current_user
)
from flask import current_app

from .password import PasswordError


class TokenError(Exception):
    """Base exception for token-related errors."""
    pass


class TokenExpiredError(TokenError):
    """Raised when a token has expired."""
    pass


class TokenInvalidError(TokenError):
    """Raised when a token is invalid or malformed."""
    pass


class TokenRevokedError(TokenError):
    """Raised when a token has been revoked."""
    pass


def create_tokens(
    user_id: uuid.UUID,
    username: str,
    role: str,
    additional_claims: Optional[Dict[str, Any]] = None
) -> Tuple[str, str]:
    """
    Create access and refresh tokens for a user.
    
    Args:
        user_id: Unique user identifier (UUID)
        username: User's username
        role: User's role (Admin, Election_Officer, etc.)
        additional_claims: Optional additional claims to include in tokens
        
    Returns:
        Tuple[str, str]: (access_token, refresh_token)
        
    Raises:
        TokenError: If token creation fails
    """
    try:
        # Prepare identity claim
        identity = str(user_id)
        
        # Prepare claims
        claims = {
            'username': username,
            'role': role,
            'type': 'access'
        }
        
        if additional_claims:
            claims.update(additional_claims)
        
        # Create access token (15 minutes expiry)
        access_token = create_access_token(
            identity=identity,
            additional_claims=claims,
            expires_delta=timedelta(minutes=15)
        )
        
        # Create refresh token (7 days expiry)
        refresh_claims = claims.copy()
        refresh_claims['type'] = 'refresh'
        refresh_token = create_refresh_token(
            identity=identity,
            additional_claims=refresh_claims,
            expires_delta=timedelta(days=7)
        )
        
        return access_token, refresh_token
        
    except Exception as e:
        raise TokenError(f"Failed to create tokens: {e}")


def decode_jwt_token(token: str) -> Dict[str, Any]:
    """
    Decode a JWT token without verification.
    
    Args:
        token: JWT token string
        
    Returns:
        Dict[str, Any]: Decoded token claims
        
    Raises:
        TokenInvalidError: If token is malformed or cannot be decoded
    """
    try:
        return decode_token(token)
    except Exception as e:
        raise TokenInvalidError(f"Failed to decode token: {e}")


def get_token_identity() -> Optional[uuid.UUID]:
    """
    Get the current user's identity from the JWT token.
    
    Returns:
        Optional[uuid.UUID]: User ID if authenticated, None otherwise
        
    Raises:
        TokenInvalidError: If identity claim is invalid
    """
    try:
        identity_str = get_jwt_identity()
        if identity_str is None:
            return None
        
        # Convert string identity back to UUID
        return uuid.UUID(identity_str)
        
    except (ValueError, AttributeError) as e:
        raise TokenInvalidError(f"Invalid identity claim: {e}")


def get_token_claims() -> Dict[str, Any]:
    """
    Get all claims from the current JWT token.
    
    Returns:
        Dict[str, Any]: Current token claims
        
    Raises:
        TokenError: If no valid token in context
    """
    try:
        jwt_data = get_jwt()
        return jwt_data
    except Exception as e:
        raise TokenError(f"Failed to get token claims: {e}")


def get_current_user_role() -> Optional[str]:
    """
    Get the current user's role from JWT claims.
    
    Returns:
        Optional[str]: User role if authenticated, None otherwise
    """
    try:
        claims = get_token_claims()
        return claims.get('role')
    except TokenError:
        return None


def is_token_expired(token: str) -> bool:
    """
    Check if a token has expired.
    
    Args:
        token: JWT token string
        
    Returns:
        bool: True if token is expired, False otherwise
        
    Raises:
        TokenInvalidError: If token is malformed
    """
    try:
        decoded = decode_token(token)
        exp_timestamp = decoded.get('exp')
        
        if exp_timestamp is None:
            return False
        
        # Convert expiration timestamp to datetime
        exp_datetime = datetime.utcfromtimestamp(exp_timestamp)
        current_datetime = datetime.utcnow()
        
        return exp_datetime < current_datetime
        
    except Exception as e:
        raise TokenInvalidError(f"Failed to check token expiration: {e}")


def get_token_expiry(token: str) -> Optional[datetime]:
    """
    Get the expiration datetime of a token.
    
    Args:
        token: JWT token string
        
    Returns:
        Optional[datetime]: Expiration datetime if available, None otherwise
        
    Raises:
        TokenInvalidError: If token is malformed
    """
    try:
        decoded = decode_token(token)
        exp_timestamp = decoded.get('exp')
        
        if exp_timestamp is None:
            return None
        
        return datetime.utcfromtimestamp(exp_timestamp)
        
    except Exception as e:
        raise TokenInvalidError(f"Failed to get token expiry: {e}")


def create_access_token_from_refresh(refresh_token: str) -> str:
    """
    Create a new access token from a valid refresh token.
    
    Args:
        refresh_token: Valid refresh token
        
    Returns:
        str: New access token
        
    Raises:
        TokenExpiredError: If refresh token has expired
        TokenInvalidError: If refresh token is invalid
        TokenError: If token creation fails
    """
    try:
        # Decode refresh token to get identity and claims
        decoded = decode_token(refresh_token)
        
        # Check if token is a refresh token
        if decoded.get('type') != 'refresh':
            raise TokenInvalidError("Token is not a refresh token")
        
        # Check expiration
        exp_timestamp = decoded.get('exp')
        if exp_timestamp:
            exp_datetime = datetime.utcfromtimestamp(exp_timestamp)
            if exp_datetime < datetime.utcnow():
                raise TokenExpiredError("Refresh token has expired")
        
        # Get identity
        identity = decoded.get('sub')
        if not identity:
            raise TokenInvalidError("Missing identity claim in refresh token")
        
        # Get other claims
        username = decoded.get('username')
        role = decoded.get('role')
        
        # Prepare claims for new access token
        claims = {
            'username': username,
            'role': role,
            'type': 'access',
            'refreshed_from': decoded.get('jti')  # Original token ID
        }
        
        # Create new access token
        return create_access_token(
            identity=identity,
            additional_claims=claims,
            expires_delta=timedelta(minutes=15)
        )
        
    except TokenExpiredError:
        raise
    except TokenInvalidError:
        raise
    except Exception as e:
        raise TokenError(f"Failed to create access token from refresh token: {e}")


# Token blacklist management (in-memory for demonstration)
# In production, use Redis or database for token blacklisting
_token_blacklist = set()


def revoke_token(token_id: str) -> None:
    """
    Revoke a token by adding it to the blacklist.
    
    Args:
        token_id: JWT ID (jti) of the token to revoke
    """
    _token_blacklist.add(token_id)


def is_token_revoked(token_id: str) -> bool:
    """
    Check if a token has been revoked.
    
    Args:
        token_id: JWT ID (jti) to check
        
    Returns:
        bool: True if token is revoked, False otherwise
    """
    return token_id in _token_blacklist


def clear_token_blacklist() -> None:
    """Clear all revoked tokens from blacklist."""
    _token_blacklist.clear()