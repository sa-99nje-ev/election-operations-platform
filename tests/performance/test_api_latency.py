import time
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.metrics_builder import PerformanceMetricsBuilder

@pytest.mark.asyncio
async def test_api_health_latency():
    builder = PerformanceMetricsBuilder("API Health & Latency", warmup_count=2)
    iterations = 20
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        t_start = time.perf_counter()
        for i in range(iterations + 2):
            t0 = time.perf_counter()
            response = await ac.get("/health")
            lat = (time.perf_counter() - t0) * 1000.0
            
            builder.add_sample(
                latency_ms=lat,
                success=(response.status_code == 200)
            )
            
        duration = time.perf_counter() - t_start
        metrics = builder.finish(duration)
        print(f"\n{metrics.export_markdown()}")
        assert metrics.confirmation_latency_p95_ms <= 1000.0
        assert metrics.success_rate_pct >= 99.99
