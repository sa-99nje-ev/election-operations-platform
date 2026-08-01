"""
Configuration management package for Election Operations Platform.

This package provides environment-based configuration following the 12-factor
app methodology. All configuration is loaded from environment variables or
a .env file.

Usage:
    from app.config import get_config
    
    # Get configuration for current environment
    config = get_config()
    
    # Or specify environment explicitly
    config = get_config('production')
    
    # Use with Flask app
    app.config.from_object(config)
"""

from .settings import (
    Config,
    DevelopmentConfig,
    TestingConfig,
    ProductionConfig,
    get_config,
    config_profiles,
    ConfigurationError
)

__all__ = [
    'Config',
    'DevelopmentConfig',
    'TestingConfig',
    'ProductionConfig',
    'get_config',
    'config_profiles',
    'ConfigurationError'
]
