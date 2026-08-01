"""
Unit tests for configuration management.

Tests that configuration classes properly load from environment variables,
validate required variables, and handle different environment profiles.
"""

import os
import pytest
from datetime import timedelta
from app.config import (
    Config,
    DevelopmentConfig,
    TestingConfig,
    ProductionConfig,
    get_config,
    ConfigurationError
)


class TestConfigBase:
    """Test base configuration class."""
    
    def test_required_vars_validation(self, monkeypatch):
        """Test that missing required variables cause exit."""
        # Clear required environment variables
        for var in Config.REQUIRED_VARS:
            monkeypatch.delenv(var, raising=False)
        
        # Attempting to instantiate should exit
        with pytest.raises(SystemExit) as exc_info:
            Config()
        
        # Should exit with non-zero status
        assert exc_info.value.code == 1
    
    def test_config_loads_from_environment(self, monkeypatch):
        """Test that configuration loads values from environment variables."""
        # Set required environment variables
        test_values = {
            'DATABASE_URL': 'postgresql://test:test@localhost/testdb',
            'REDIS_URL': 'redis://localhost:6379/0',
            'SECRET_KEY': 'test-secret-key',
            'JWT_SECRET_KEY': 'test-jwt-secret'
        }
        
        for key, value in test_values.items():
            monkeypatch.setenv(key, value)
        
        # Create config instance
        config = Config()
        
        # Verify values are loaded
        assert config.SQLALCHEMY_DATABASE_URI == test_values['DATABASE_URL']
        assert config.REDIS_URL == test_values['REDIS_URL']
        assert config.SECRET_KEY == test_values['SECRET_KEY']
        assert config.JWT_SECRET_KEY == test_values['JWT_SECRET_KEY']
    
    def test_jwt_token_expiry_defaults(self, monkeypatch):
        """Test JWT token expiry defaults."""
        # Set required vars
        for var in Config.REQUIRED_VARS:
            monkeypatch.setenv(var, 'test-value')
        
        config = Config()
        
        # Check defaults
        assert config.JWT_ACCESS_TOKEN_EXPIRES == timedelta(seconds=900)  # 15 minutes
        assert config.JWT_REFRESH_TOKEN_EXPIRES == timedelta(seconds=604800)  # 7 days
    
    def test_jwt_token_expiry_custom_values(self, monkeypatch):
        """Test JWT token expiry with custom values."""
        # Set required vars
        for var in Config.REQUIRED_VARS:
            monkeypatch.setenv(var, 'test-value')
        
        # Set custom expiry values
        monkeypatch.setenv('JWT_ACCESS_TOKEN_EXPIRES', '600')  # 10 minutes
        monkeypatch.setenv('JWT_REFRESH_TOKEN_EXPIRES', '86400')  # 1 day
        
        config = Config()
        
        # Check custom values
        assert config.JWT_ACCESS_TOKEN_EXPIRES == timedelta(seconds=600)
        assert config.JWT_REFRESH_TOKEN_EXPIRES == timedelta(seconds=86400)
    
    def test_celery_configuration(self, monkeypatch):
        """Test Celery configuration defaults."""
        # Set required vars
        for var in Config.REQUIRED_VARS:
            monkeypatch.setenv(var, 'test-value')
        
        monkeypatch.setenv('REDIS_URL', 'redis://localhost:6379/0')
        
        config = Config()
        
        # Check Celery defaults
        assert config.CELERY_BROKER_URL == 'redis://localhost:6379/0'
        assert config.CELERY_RESULT_BACKEND == 'redis://localhost:6379/0'
        assert config.CELERY_WORKER_CONCURRENCY == 4
        assert config.CELERY_TASK_TIME_LIMIT == 30
    
    def test_service_port_defaults(self, monkeypatch):
        """Test service port defaults."""
        # Set required vars
        for var in Config.REQUIRED_VARS:
            monkeypatch.setenv(var, 'test-value')
        
        config = Config()
        
        # Check port defaults
        assert config.API_PORT == 5000
        assert config.DASHBOARD_PORT == 8050
        assert config.LOCUST_PORT == 8089


class TestDevelopmentConfig:
    """Test development configuration profile."""
    
    def test_development_config_debug_enabled(self, monkeypatch):
        """Test that debug mode is enabled in development."""
        # Set required vars
        for var in Config.REQUIRED_VARS:
            monkeypatch.setenv(var, 'test-value')
        
        config = DevelopmentConfig()
        
        assert config.DEBUG is True
        assert config.TESTING is False
    
    def test_development_config_sqlalchemy_echo(self, monkeypatch):
        """Test SQLAlchemy echo configuration in development."""
        # Set required vars
        for var in Config.REQUIRED_VARS:
            monkeypatch.setenv(var, 'test-value')
        
        # Test default (False)
        config = DevelopmentConfig()
        assert config.SQLALCHEMY_ECHO is False
        
        # Test with SQLALCHEMY_ECHO=True
        monkeypatch.setenv('SQLALCHEMY_ECHO', 'true')
        config = DevelopmentConfig()
        assert config.SQLALCHEMY_ECHO is True


class TestTestingConfig:
    """Test testing configuration profile."""
    
    def test_testing_config_flags(self, monkeypatch):
        """Test that testing flags are set correctly."""
        # Set required vars
        for var in Config.REQUIRED_VARS:
            monkeypatch.setenv(var, 'test-value')
        
        config = TestingConfig()
        
        assert config.TESTING is True
        assert config.DEBUG is True
    
    def test_testing_config_faster_jwt_expiry(self, monkeypatch):
        """Test that testing uses shorter JWT token expiry."""
        # Set required vars
        for var in Config.REQUIRED_VARS:
            monkeypatch.setenv(var, 'test-value')
        
        config = TestingConfig()
        
        # Testing should have shorter expiry for faster tests
        assert config.JWT_ACCESS_TOKEN_EXPIRES == timedelta(seconds=300)  # 5 minutes
        assert config.JWT_REFRESH_TOKEN_EXPIRES == timedelta(seconds=3600)  # 1 hour
    
    def test_testing_config_test_database_url(self, monkeypatch):
        """Test that testing can use separate test database."""
        # Set required vars
        for var in Config.REQUIRED_VARS:
            monkeypatch.setenv(var, 'test-value')
        
        monkeypatch.setenv('DATABASE_URL', 'postgresql://prod:prod@localhost/prod_db')
        monkeypatch.setenv('TEST_DATABASE_URL', 'postgresql://test:test@localhost/test_db')
        
        config = TestingConfig()
        
        # Should use test database URL
        assert config.SQLALCHEMY_DATABASE_URI == 'postgresql://test:test@localhost/test_db'


class TestProductionConfig:
    """Test production configuration profile."""
    
    def test_production_config_debug_disabled(self, monkeypatch):
        """Test that debug mode is disabled in production."""
        # Set required vars
        for var in Config.REQUIRED_VARS:
            monkeypatch.setenv(var, 'test-value')
        
        config = ProductionConfig()
        
        assert config.DEBUG is False
        assert config.TESTING is False
    
    def test_production_config_security_settings(self, monkeypatch):
        """Test production security settings."""
        # Set required vars
        for var in Config.REQUIRED_VARS:
            monkeypatch.setenv(var, 'test-value')
        
        config = ProductionConfig()
        
        # Check security settings
        assert config.SESSION_COOKIE_SECURE is True
        assert config.SESSION_COOKIE_HTTPONLY is True
        assert config.SESSION_COOKIE_SAMESITE == 'Lax'
        assert config.SQLALCHEMY_ECHO is False


class TestGetConfig:
    """Test get_config function."""
    
    def test_get_config_development_default(self, monkeypatch):
        """Test that development is default environment."""
        # Set required vars
        for var in Config.REQUIRED_VARS:
            monkeypatch.setenv(var, 'test-value')
        
        # Clear FLASK_ENV
        monkeypatch.delenv('FLASK_ENV', raising=False)
        
        config = get_config()
        
        assert isinstance(config, DevelopmentConfig)
    
    def test_get_config_from_flask_env(self, monkeypatch):
        """Test that FLASK_ENV variable is used."""
        # Set required vars
        for var in Config.REQUIRED_VARS:
            monkeypatch.setenv(var, 'test-value')
        
        # Test each environment
        monkeypatch.setenv('FLASK_ENV', 'production')
        config = get_config()
        assert isinstance(config, ProductionConfig)
        
        monkeypatch.setenv('FLASK_ENV', 'testing')
        config = get_config()
        assert isinstance(config, TestingConfig)
        
        monkeypatch.setenv('FLASK_ENV', 'development')
        config = get_config()
        assert isinstance(config, DevelopmentConfig)
    
    def test_get_config_explicit_env(self, monkeypatch):
        """Test that explicit environment parameter works."""
        # Set required vars
        for var in Config.REQUIRED_VARS:
            monkeypatch.setenv(var, 'test-value')
        
        # Explicit environment should override FLASK_ENV
        monkeypatch.setenv('FLASK_ENV', 'development')
        
        config = get_config('production')
        assert isinstance(config, ProductionConfig)
        
        config = get_config('testing')
        assert isinstance(config, TestingConfig)
    
    def test_get_config_case_insensitive(self, monkeypatch):
        """Test that environment names are case insensitive."""
        # Set required vars
        for var in Config.REQUIRED_VARS:
            monkeypatch.setenv(var, 'test-value')
        
        # Test various cases
        config = get_config('PRODUCTION')
        assert isinstance(config, ProductionConfig)
        
        config = get_config('Production')
        assert isinstance(config, ProductionConfig)
        
        config = get_config('  production  ')
        assert isinstance(config, ProductionConfig)
    
    def test_get_config_unknown_env_defaults_to_development(self, monkeypatch):
        """Test that unknown environment falls back to development."""
        # Set required vars
        for var in Config.REQUIRED_VARS:
            monkeypatch.setenv(var, 'test-value')
        
        config = get_config('unknown-environment')
        assert isinstance(config, DevelopmentConfig)
