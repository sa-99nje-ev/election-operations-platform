"""
Pydantic v2 schemas for Authentication requests and responses.
"""

from pydantic import BaseModel, ConfigDict


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: str
    username: str
    role: str

    model_config = ConfigDict(from_attributes=True)