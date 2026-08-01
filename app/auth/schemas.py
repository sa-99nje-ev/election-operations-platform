"""
Authentication schemas for request/response validation.

This module defines Pydantic/FastAPI-style schemas for authentication requests
and responses. In a Flask application, these can be used with libraries like
marshmallow or directly for validation.
"""

from typing import Optional
from pydantic import BaseModel, Field, validator
import re


class LoginRequest(BaseModel):
    """Schema for login requests."""
    
    username: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="User's login username"
    )
    
    password: str = Field(
        ...,
        min_length=12,
        max_length=128,
        description="User's password"
    )
    
    @validator('username')
    def validate_username(cls, v):
        """Validate username format."""
        if not v.strip():
            raise ValueError("Username cannot be empty or whitespace")
        
        # Username should be alphanumeric with underscores
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError(
                "Username can only contain letters, numbers, and underscores"
            )
        
        return v.strip()
    
    @validator('password')
    def validate_password_not_empty(cls, v):
        """Validate password is not empty."""
        if not v.strip():
            raise ValueError("Password cannot be empty")
        return v


class LoginResponse(BaseModel):
    """Schema for successful login responses."""
    
    access_token: str = Field(
        ...,
        description="JWT access token (15 minute expiry)"
    )
    
    refresh_token: str = Field(
        ...,
        description="JWT refresh token (7 day expiry)"
    )
    
    token_type: str = Field(
        default="bearer",
        description="Token type (always 'bearer')"
    )
    
    expires_in: int = Field(
        default=900,
        description="Access token expiry in seconds (900 = 15 minutes)"
    )


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token requests."""
    
    refresh_token: str = Field(
        ...,
        description="Valid refresh token"
    )


class RefreshTokenResponse(BaseModel):
    """Schema for refresh token responses."""
    
    access_token: str = Field(
        ...,
        description="New JWT access token (15 minute expiry)"
    )
    
    token_type: str = Field(
        default="bearer",
        description="Token type (always 'bearer')"
    )
    
    expires_in: int = Field(
        default=900,
        description="Access token expiry in seconds (900 = 15 minutes)"
    )


class LogoutRequest(BaseModel):
    """Schema for logout requests."""
    
    refresh_token: str = Field(
        ...,
        description="Refresh token to invalidate"
    )


class LogoutResponse(BaseModel):
    """Schema for logout responses."""
    
    message: str = Field(
        default="Successfully logged out",
        description="Logout confirmation message"
    )


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    
    error: dict = Field(
        ...,
        description="Error details"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "error": {
                    "code": "AUTH_FAILED",
                    "message": "Authentication failed"
                }
            }
        }


class TokenInfo(BaseModel):
    """Schema for token information."""
    
    user_id: str = Field(
        ...,
        description="User ID from token"
    )
    
    username: str = Field(
        ...,
        description="Username from token"
    )
    
    role: str = Field(
        ...,
        description="User role from token"
    )
    
    issued_at: Optional[int] = Field(
        None,
        description="Token issuance timestamp"
    )
    
    expires_at: Optional[int] = Field(
        None,
        description="Token expiration timestamp"
    )


class PasswordChangeRequest(BaseModel):
    """Schema for password change requests."""
    
    current_password: str = Field(
        ...,
        min_length=12,
        max_length=128,
        description="Current password"
    )
    
    new_password: str = Field(
        ...,
        min_length=12,
        max_length=128,
        description="New password"
    )
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password meets complexity requirements."""
        from app.utils.password import is_password_strong
        
        is_valid, error_message = is_password_strong(v)
        if not is_valid:
            raise ValueError(error_message)
        
        return v


class PasswordChangeResponse(BaseModel):
    """Schema for password change responses."""
    
    message: str = Field(
        default="Password successfully changed",
        description="Password change confirmation message"
    )


# Common error codes for authentication
AUTH_ERROR_CODES = {
    "INVALID_CREDENTIALS": "Invalid username or password",
    "TOKEN_EXPIRED": "Access token has expired",
    "TOKEN_INVALID": "Invalid or malformed token",
    "TOKEN_REVOKED": "Token has been revoked",
    "REFRESH_TOKEN_INVALID": "Invalid refresh token",
    "REFRESH_TOKEN_EXPIRED": "Refresh token has expired",
    "PERMISSION_DENIED": "User does not have permission to access this resource",
    "USER_DISABLED": "User account is disabled",
    "PASSWORD_TOO_WEAK": "Password does not meet complexity requirements",
    "PASSWORD_MISMATCH": "Current password is incorrect",
    "ACCOUNT_LOCKED": "Account is locked due to too many failed attempts",
}


def create_error_response(error_code: str, message: Optional[str] = None) -> dict:
    """
    Create a standardized error response.
    
    Args:
        error_code: Error code from AUTH_ERROR_CODES
        message: Optional custom message (uses default if not provided)
        
    Returns:
        dict: Standardized error response
    """
    error_message = message or AUTH_ERROR_CODES.get(error_code, "Unknown error")
    
    return {
        "error": {
            "code": error_code,
            "message": error_message
        }
    }