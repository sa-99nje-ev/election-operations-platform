"""
JWT token management utilities for authentication and authorization.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Tuple

from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token
)


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
    """Create access and refresh token pair for user."""
    try:
        claims = {
            'sub': username,
            'user_id': str(user_id),
            'role': role
        }
        if additional_claims:
            claims.update(additional_claims)

        access_token = create_access_token(
            data=claims,
            expires_delta=timedelta(minutes=15)
        )
        
        refresh_claims = claims.copy()
        refresh_token = create_refresh_token(
            data=refresh_claims,
            expires_delta=timedelta(days=7)
        )

        return access_token, refresh_token

    except Exception as e:
        raise TokenError(f"Failed to create tokens: {e}")


def decode_jwt_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token payload."""
    payload = decode_token(token)
    if not payload:
        raise TokenInvalidError("Failed to decode token or token invalid")
    return payload


def is_token_expired(token: str) -> bool:
    """Check if a token has passed its expiration time."""
    try:
        payload = decode_jwt_token(token)
        exp = payload.get('exp')
        if not exp:
            return False
        return datetime.fromtimestamp(exp, timezone.utc) < datetime.now(timezone.utc)
    except Exception as e:
        raise TokenInvalidError(f"Failed to check token expiration: {e}")


def create_access_token_from_refresh(refresh_token: str) -> str:
    """Create a new access token from a valid refresh token."""
    payload = decode_jwt_token(refresh_token)
    if payload.get('type') != 'refresh':
        raise TokenInvalidError("Token is not a valid refresh token")

    if is_token_expired(refresh_token):
        raise TokenExpiredError("Refresh token has expired")

    username = payload.get('sub')
    role = payload.get('role')

    if not username or not role:
        raise TokenInvalidError("Missing essential claims in refresh token")

    return create_access_token(
        data={'sub': username, 'role': role},
        expires_delta=timedelta(minutes=15)
    )


# Token Blacklist Management
_token_blacklist = set()


def revoke_token(token_id: str) -> None:
    """Revoke a token by adding its unique identifier (jti) to the blacklist."""
    _token_blacklist.add(token_id)


def is_token_revoked(token_id: str) -> bool:
    """Check if a token identifier has been revoked."""
    return token_id in _token_blacklist


def clear_token_blacklist() -> None:
    """Clear all revoked tokens from memory."""
    _token_blacklist.clear()