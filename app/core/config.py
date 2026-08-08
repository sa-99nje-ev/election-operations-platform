import os

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class PerformanceSettings(BaseSettings):
    DEPLOYMENT_PROFILE: str = os.getenv(
        "DEPLOYMENT_PROFILE",
        "LOCAL_DEV"
    )

    DB_COMMIT_SLO_MS: float = 500.0
    API_P95_SLO_MS: float = 1000.0
    MIN_RPS_SLO: float = 2.0
    MAX_QUEUE_PEAK: int = 500

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://election_user:local_password@localhost:5432/election_db"
    )

    model_config = ConfigDict(
        env_file=".env",
        extra="ignore"
    )


def get_performance_settings() -> PerformanceSettings:
    settings = PerformanceSettings()

    profile = settings.DEPLOYMENT_PROFILE.upper()

    if profile == "PRODUCTION":
        settings.DB_COMMIT_SLO_MS = 100.0
        settings.API_P95_SLO_MS = 200.0
        settings.MIN_RPS_SLO = 100.0

    elif profile == "STAGING":
        settings.DB_COMMIT_SLO_MS = 250.0
        settings.API_P95_SLO_MS = 500.0
        settings.MIN_RPS_SLO = 20.0

    else:
        settings.DB_COMMIT_SLO_MS = 500.0
        settings.API_P95_SLO_MS = 1000.0
        settings.MIN_RPS_SLO = 2.0

    return settings


perf_settings = get_performance_settings()
settings = perf_settings
