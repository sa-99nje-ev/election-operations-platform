"""
Authentication and authorization package.

This package contains modules for user authentication, JWT token management,
RBAC (Role-Based Access Control), and related functionality.
"""

from .routes import auth_bp
from .schemas import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    LogoutRequest,
    LogoutResponse,
    PasswordChangeRequest,
    PasswordChangeResponse,
    ErrorResponse,
    TokenInfo,
    AUTH_ERROR_CODES,
    create_error_response
)

__all__ = [
    'auth_bp',
    'LoginRequest',
    'LoginResponse',
    'RefreshTokenRequest',
    'RefreshTokenResponse',
    'LogoutRequest',
    'LogoutResponse',
    'PasswordChangeRequest',
    'PasswordChangeResponse',
    'ErrorResponse',
    'TokenInfo',
    'AUTH_ERROR_CODES',
    'create_error_response',
]
