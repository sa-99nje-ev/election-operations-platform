"""Testing environment configuration."""

import os
from datetime import timedelta
from app.config.settings import Config


class TestingConfig(Config):
    """Automated testing environment settings."""

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL",
        "sqlite:///:memory:"
    )
    WTF_CSRF_ENABLED = False
    BCRYPT_LOG_ROUNDS = 4
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=300)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=3600)
    LOG_LEVEL = "WARNING"