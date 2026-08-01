"""
Alembic environment configuration for Election Operations Platform.

This module configures Alembic migrations to work with the Flask-SQLAlchemy
application. It imports all models and sets up database connection using
the Flask app configuration.
"""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import Flask app and extensions
from app import create_app
from app.extensions import db

# Import all models so Alembic can detect them for autogeneration
from app.models import (
    User,
    Constituency,
    Voter,
    Candidate,
    PollingBooth,
    VotingRecord,
    AuditLog,
    RefreshToken,
)

# Alembic Config object provides access to .ini file values
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Create Flask app to access configuration
app = create_app()

# Function to get database URL from Flask config
def get_url():
    """
    Retrieve database URL from Flask application configuration.
    
    Returns:
        Database URL string from SQLALCHEMY_DATABASE_URI config.
    """
    with app.app_context():
        return app.config['SQLALCHEMY_DATABASE_URI']

# Set target metadata for autogenerate support
target_metadata = db.Model.metadata

# Other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # Detect column type changes
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # Override sqlalchemy.url with value from Flask config
    configuration = config.get_section(config.config_ini_section)
    configuration['sqlalchemy.url'] = get_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # Enable type comparison for autogenerate
        )

        with context.begin_transaction():
            context.run_migrations()


# Determine which mode to run migrations in
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
