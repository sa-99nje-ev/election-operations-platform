"""
Unit tests for domain services using AsyncSession.
"""

import pytest
from unittest.mock import AsyncMock
from app.services.voting_service import VotingService


@pytest.mark.asyncio
async def test_voting_service_instantiation():
    mock_session = AsyncMock()
    service = VotingService(
        session=mock_session,
        voting_record_repo=AsyncMock(),
        voter_repo=AsyncMock(),
        candidate_repo=AsyncMock(),
        booth_repo=AsyncMock(),
        audit_log_repo=AsyncMock()
    )
    assert service is not None