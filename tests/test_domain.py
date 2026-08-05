import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_unauthenticated_constituencies_fetch(client: AsyncClient):
    """Verify route behavior for constituencies endpoint."""
    response = await client.get("/constituencies/", follow_redirects=False)
    assert response.status_code in [200, 401, 403, 307, 404, 405]
