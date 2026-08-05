"""Development environment configuration."""

import os
from app.config.settings import Config


class DevelopmentConfig(Config):
    """Development settings with local overrides."""

    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = False
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")