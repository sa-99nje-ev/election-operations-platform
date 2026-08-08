"""
Modern unit test suite for ARQ Worker using Factory Boy and Async SQLite.
"""

import uuid
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from unittest.mock import patch

import app.models  # Force-load SQLAlchemy mapper registry
from app.database import Base
from app.workers.voting_worker import process_vote_task
from tests.factories import PollingBoothFactory


@pytest_asyncio.fixture
async def in_memory_db():
    """Isolated, zero-friction in-memory database context."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    yield session_factory

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.mark.asyncio
async def test_process_vote_task_execution(in_memory_db):
    booth_id = uuid.uuid4()
    voter_id = uuid.uuid4()
    candidate_id = uuid.uuid4()

    # Generate a schema-compliant booth using Factory Boy
    booth = PollingBoothFactory(id=booth_id, status="OPEN")

    async with in_memory_db() as session:
        session.add(booth)
        await session.commit()

    vote_payload = {
        "request_id": str(uuid.uuid4()),
        "trace_id": str(uuid.uuid4()),
        "voter_id": str(voter_id),
        "candidate_id": str(candidate_id),
        "booth_id": str(booth_id)
    }

    with patch("app.workers.voting_worker.AsyncSessionLocal", in_memory_db):
        result = await process_vote_task({}, vote_payload)

    assert result["status"] == "SUCCESS"
    assert result["request_id"] == vote_payload["request_id"]
