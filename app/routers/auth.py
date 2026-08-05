"""
Authentication router using ServiceFactory and clean error handling.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.factories import ServiceFactory
from app.schemas.auth import TokenResponse

router = APIRouter(
    tags=["Auth"],
    responses={
        401: {"description": "Not authenticated or invalid credentials"},
        422: {"description": "Validation Error"},
    },
)


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={
        401: {"description": "Invalid username or password"},
        422: {"description": "Validation Error"},
    },
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user and return JWT tokens cleanly."""
    auth_service = ServiceFactory.get_auth_service(db)
    token = await auth_service.login(
        username=form_data.username,
        password=form_data.password
    )
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token
