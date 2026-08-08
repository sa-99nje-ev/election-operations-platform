import os
import sys
import asyncio
from logging.config import fileConfig

from dotenv import load_dotenv
from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

load_dotenv()

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from app.database import Base
from app.models.user import User
from app.models.constituency import Constituency
from app.models.voter import Voter
from app.models.candidate import Candidate
from app.models.polling_booth import PollingBooth
from app.models.voting_record import VotingRecord
from app.models.audit_log import AuditLog
from app.models.refresh_token import RefreshToken

config = context.config

if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    config.set_main_option("sqlalchemy.url", DATABASE_URL)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    configuration = config.get_section(config.config_ini_section)

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
