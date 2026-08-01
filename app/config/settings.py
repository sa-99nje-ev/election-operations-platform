"""
Configuration settings module for the Election Operations Platform.

This module provides environment-based configuration classes following the
12-factor app methodology. All configuration is loaded from environment
variables or a .env file.

Required environment variables:
    - DATABASE_URL: PostgreSQL connection string
    - REDIS_URL: Redis connection string
    - SECRET_KEY: Flask secret key for session management
    - JWT_SECRET_KEY: Secret key for JWT token signing

Optional environment variables with defaults:
    - FLASK_ENV: Application environment (development/testing/production)
    - JWT_ACCESS_TOKEN_EXPIRES: Access token expiry in seconds (default: 900)
    - JWT_REFRESH_TOKEN_EXPIRES: Refresh token expiry in seconds (default: 604800)
    - CELERY_BROKER_URL: Celery broker URL (defaults to REDIS_URL)
    - CELERY_RESULT_BACKEND: Celery result backend URL (defaults to REDIS_URL)
    - CELERY_WORKER_CONCURRENCY: Number of worker processes (default: 4)
    - API_PORT: API server port (default: 5000)
    - DASHBOARD_PORT: Dashboard server port (default: 8050)
    - LOCUST_PORT: Locust web UI port (default: 8089)
    - ELECTION_START_TIME: Election day start time (ISO 8601 format)
    - ELECTION_END_TIME: Election day end time (ISO 8601 format)
"""

import os
import sys
from datetime import timedelta
from typing import Optional


class ConfigurationError(Exception):
    """Raised when required configuration is missing or invalid."""
    pass


class Config:
    """
    Base configuration class.
    
    Loads all settings from environment variables. Validates that required
    variables are present and exits with descriptive error messages if any
    are missing.
    """
    
    # Required configuration variables
    REQUIRED_VARS = [
        'DATABASE_URL',
        'REDIS_URL',
        'SECRET_KEY',
        'JWT_SECRET_KEY'
    ]
    
    def __init__(self):
        """Initialize configuration and validate required variables."""
        self._validate_required_vars()
    
    @classmethod
    def _validate_required_vars(cls):
        """
        Validate that all required environment variables are present.
        
        Raises:
            SystemExit: If any required variable is missing, exits with
                       descriptive error message listing all missing variables.
        """
        missing_vars = []
        for var in cls.REQUIRED_VARS:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            error_message = (
                "\n" + "=" * 70 + "\n"
                "CONFIGURATION ERROR: Required environment variables are missing\n"
                "=" * 70 + "\n\n"
                "The following required environment variables are not set:\n\n"
            )
            for var in missing_vars:
                error_message += f"  - {var}\n"
            
            error_message += (
                "\nPlease set these variables in your environment or .env file.\n"
                "See .env.example for required configuration format.\n"
                "=" * 70 + "\n"
            )
            
            print(error_message, file=sys.stderr)
            sys.exit(1)
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.getenv('DB_POOL_SIZE', '5')),
        'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', '3600')),
        'pool_pre_ping': True,  # Verify connections before using
    }
    
    # Redis Configuration
    REDIS_URL = os.getenv('REDIS_URL')
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '900'))  # 15 minutes
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', '604800'))  # 7 days
    )
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # Celery Configuration
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', os.getenv('REDIS_URL'))
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', os.getenv('REDIS_URL'))
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = 'UTC'
    CELERY_ENABLE_UTC = True
    CELERY_TASK_TIME_LIMIT = int(os.getenv('CELERY_TASK_TIME_LIMIT', '30'))
    CELERY_WORKER_CONCURRENCY = int(os.getenv('CELERY_WORKER_CONCURRENCY', '4'))
    CELERY_WORKER_PREFETCH_MULTIPLIER = int(
        os.getenv('CELERY_WORKER_PREFETCH_MULTIPLIER', '1')
    )
    
    # Service Port Configuration
    API_PORT = int(os.getenv('API_PORT', '5000'))
    DASHBOARD_PORT = int(os.getenv('DASHBOARD_PORT', '8050'))
    LOCUST_PORT = int(os.getenv('LOCUST_PORT', '8089'))
    
    # Election Day Configuration
    ELECTION_START_TIME: Optional[str] = os.getenv('ELECTION_START_TIME')
    ELECTION_END_TIME: Optional[str] = os.getenv('ELECTION_END_TIME')
    
    # Application Configuration
    TESTING = False
    DEBUG = False
    JSON_SORT_KEYS = False
    
    # Pagination
    DEFAULT_PAGE_SIZE = int(os.getenv('DEFAULT_PAGE_SIZE', '20'))
    MAX_PAGE_SIZE = int(os.getenv('MAX_PAGE_SIZE', '100'))
    
    # Audit Log Configuration
    AUDIT_LOG_RETRY_ATTEMPTS = int(os.getenv('AUDIT_LOG_RETRY_ATTEMPTS', '3'))
    AUDIT_LOG_RETRY_DELAY = int(os.getenv('AUDIT_LOG_RETRY_DELAY', '1'))


class DevelopmentConfig(Config):
    """
    Development environment configuration.
    
    Enables debug mode and relaxed settings for local development.
    """
    
    DEBUG = True
    
    # More verbose logging in development
    SQLALCHEMY_ECHO = os.getenv('SQLALCHEMY_ECHO', 'False').lower() == 'true'
    
    # Development-specific settings
    TESTING = False


class TestingConfig(Config):
    """
    Testing environment configuration.
    
    Uses in-memory or test databases and disables features that interfere
    with automated testing.
    """
    
    TESTING = True
    DEBUG = True
    
    # Override database for testing (if TEST_DATABASE_URL is provided)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'TEST_DATABASE_URL',
        os.getenv('DATABASE_URL')
    )
    
    # Disable CSRF protection in tests
    WTF_CSRF_ENABLED = False
    
    # Faster password hashing in tests (lower bcrypt rounds)
    BCRYPT_LOG_ROUNDS = 4  # Minimum for bcrypt
    
    # Shorter token expiry for faster test execution
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=300)  # 5 minutes
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=3600)  # 1 hour


class ProductionConfig(Config):
    """
    Production environment configuration.
    
    Strict security settings and optimized for production workloads.
    """
    
    DEBUG = False
    TESTING = False
    
    # Production-specific settings
    SQLALCHEMY_ECHO = False
    
    # Enforce HTTPS in production (for cookie security)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Additional security headers (configured at reverse proxy level)
    # but can be enabled here if needed


# Configuration profile mapping
config_profiles = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(env: Optional[str] = None) -> Config:
    """
    Get configuration object based on environment.
    
    Args:
        env: Environment name (development/testing/production).
             If None, reads from FLASK_ENV environment variable.
             Defaults to 'development' if FLASK_ENV is not set.
    
    Returns:
        Configuration object for the specified environment.
    
    Example:
        >>> config = get_config('production')
        >>> app.config.from_object(config)
    """
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    
    # Normalize environment name (lowercase, strip whitespace)
    env = env.lower().strip()
    
    # Get configuration class from profile mapping
    config_class = config_profiles.get(env, DevelopmentConfig)
    
    # Instantiate and return configuration
    return config_class()
