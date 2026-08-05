import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Verify /health endpoint status."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] in ["ok", "healthy"]
