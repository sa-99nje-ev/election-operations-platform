"""
Core security module for password hashing and JWT token generation.
Reads configuration dynamically from app.core.config to prevent secret leaks.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Any
from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# CryptContext configured with bcrypt scheme
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against an encrypted hash."""
    if not plain_password or not hashed_password:
        return False
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a secure bcrypt password hash."""
    return pwd_context.hash(password)


def create_access_token(
    data: dict[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Generate a signed JWT access token using configuration from settings.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Fall back to settings configured expiry (seconds -> timedelta) or default to 60 mins
        expires_seconds = getattr(settings, "JWT_ACCESS_TOKEN_EXPIRES", 3600)
        expire = datetime.now(timezone.utc) + timedelta(seconds=expires_seconds)
    
    to_encode.update({"exp": expire})
    
    # Use JWT_SECRET_KEY if defined, else fallback to SECRET_KEY from config
    signing_key = getattr(settings, "JWT_SECRET_KEY", settings.SECRET_KEY)
    algorithm = getattr(settings, "ALGORITHM", "HS256")
    
    encoded_jwt = jwt.encode(to_encode, signing_key, algorithm=algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict[str, Any]]:
    """
    Safely decode and validate a JWT access token.
    """
    signing_key = getattr(settings, "JWT_SECRET_KEY", settings.SECRET_KEY)
    algorithm = getattr(settings, "ALGORITHM", "HS256")
    
    try:
        payload = jwt.decode(token, signing_key, algorithms=[algorithm])
        return payload
    except jwt.JWTError:
        return None