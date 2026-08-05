import time
import pytest
import uuid
from sqlalchemy import text
from app.database import AsyncSessionLocal
from app.core.metrics_builder import PerformanceMetricsBuilder
from app.core.config import perf_settings

@pytest.mark.asyncio
async def test_database_persistence():
    builder = PerformanceMetricsBuilder("Database Persistence Operations", warmup_count=2)
    iterations = 10
    
    t_start = time.perf_counter()
    for i in range(iterations + 2):
        t0 = time.perf_counter()
        async with AsyncSessionLocal() as session:
            # Measure real transactional commit persistence with actual insert statements
            t_commit = time.perf_counter()
            await session.execute(
                text("INSERT INTO constituencies (id, name, region) VALUES (:id, :name, :region) ON CONFLICT DO NOTHING"),
                {"id": uuid.uuid4(), "name": f"Test-Dist-{i}", "region": "Central"}
            )
            await session.commit()
            commit_lat = (time.perf_counter() - t_commit) * 1000.0
            
        lat = (time.perf_counter() - t0) * 1000.0
        builder.add_sample(
            latency_ms=lat,
            db_commit_ms=commit_lat,
            success=True
        )
        
    duration = time.perf_counter() - t_start
    metrics = builder.finish(duration)
    print(f"\n{metrics.export_markdown()}")
    # Assert against environment-driven SLO configuration instead of hardcoded numbers
    assert metrics.db_commit_latency_p95_ms <= perf_settings.DB_COMMIT_SLO_MS
    assert metrics.success_rate_pct == 100.0
