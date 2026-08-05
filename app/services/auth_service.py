from datetime import timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repository import UserRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.core.security import verify_password, create_access_token
from app.schemas.auth import TokenResponse


class AuthService:
    def __init__(
        self,
        session: AsyncSession,
        user_repo: UserRepository,
        refresh_token_repo: RefreshTokenRepository,
        audit_log_repo: AuditLogRepository,
    ):
        self.session = session
        self.user_repo = user_repo
        self.refresh_token_repo = refresh_token_repo
        self.audit_log_repo = audit_log_repo

    async def login(self, username: str, password: str) -> Optional[TokenResponse]:
        user = await self.user_repo.get_by_username(username)
        if not user or not user.is_active:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role}
        )
        refresh_token = create_access_token(
            data={"sub": str(user.id), "type": "refresh"},
            expires_delta=timedelta(days=7)
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
