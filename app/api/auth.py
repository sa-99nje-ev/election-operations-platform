"""
Authentication endpoints with documented status codes and safe error handling.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
# Import your actual User model and security helpers
from app.models.user import User  
from app.core.security import verify_password, create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={
        401: {"description": "Not authenticated or invalid credentials"},
        422: {"description": "Validation Error"},
    },
)


@router.post(
    "/login",
    responses={
        200: {"description": "Successful Login"},
        401: {"description": "Invalid username or password"},
        422: {"description": "Validation Error"},
    },
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Safely handle user authentication without raising unhandled 500 errors."""
    username = (form_data.username or "").strip()
    password = (form_data.password or "").strip()

    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user = await db.scalar(select(User).where(User.username == username))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}