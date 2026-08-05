from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repository import UserRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.voter_repository import VoterRepository
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.constituency_repository import ConstituencyRepository
from app.repositories.polling_booth_repository import PollingBoothRepository
from app.repositories.voting_record_repository import VotingRecordRepository

from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.voter_service import VoterService
from app.services.candidate_service import CandidateService
from app.services.constituency_service import ConstituencyService
from app.services.polling_booth_service import PollingBoothService
from app.services.voting_service import VotingService
from app.services.results_service import ResultsService


class ServiceFactory:

    @classmethod
    def get_auth_service(cls, session: AsyncSession) -> AuthService:
        return AuthService(
            session=session,
            user_repo=UserRepository(session),
            refresh_token_repo=RefreshTokenRepository(session),
            audit_log_repo=AuditLogRepository(session)
        )

    @classmethod
    def get_user_service(cls, session: AsyncSession) -> UserService:
        return UserService(
            session=session,
            user_repo=UserRepository(session)
        )

    @classmethod
    def get_voter_service(cls, session: AsyncSession) -> VoterService:
        return VoterService(
            session=session,
            voter_repo=VoterRepository(session),
            constituency_repo=ConstituencyRepository(session)
        )

    @classmethod
    def get_candidate_service(cls, session: AsyncSession) -> CandidateService:
        return CandidateService(
            session=session,
            candidate_repo=CandidateRepository(session),
            constituency_repo=ConstituencyRepository(session)
        )

    @classmethod
    def get_constituency_service(cls, session: AsyncSession) -> ConstituencyService:
        return ConstituencyService(
            session=session,
            constituency_repo=ConstituencyRepository(session)
        )

    @classmethod
    def get_polling_booth_service(cls, session: AsyncSession) -> PollingBoothService:
        return PollingBoothService(
            session=session,
            booth_repo=PollingBoothRepository(session),
            constituency_repo=ConstituencyRepository(session)
        )

    @classmethod
    def get_voting_service(cls, session: AsyncSession) -> VotingService:
        return VotingService(
            session=session,
            voting_record_repo=VotingRecordRepository(session),
            voter_repo=VoterRepository(session),
            candidate_repo=CandidateRepository(session),
            booth_repo=PollingBoothRepository(session),
            audit_log_repo=AuditLogRepository(session)
        )

    @classmethod
    def get_results_service(cls, session: AsyncSession) -> ResultsService:
        return ResultsService(
            session=session,
            voting_record_repo=VotingRecordRepository(session),
            candidate_repo=CandidateRepository(session),
            constituency_repo=ConstituencyRepository(session)
        )
