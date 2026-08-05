"""Production environment configuration."""

import os
from app.config.settings import Config


class ProductionConfig(Config):
    """Production configuration enforcing strict security and connection pooling."""

    DEBUG = False
    TESTING = False
    SQLALCHEMY_ECHO = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")