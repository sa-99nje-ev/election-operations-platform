import time
import pytest
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings

@pytest.mark.asyncio
async def test_ballot_submission_pipeline():
    """Simple performance test using an isolated engine bound to the current event loop."""
    isolated_engine = create_async_engine(
        settings.DATABASE_URL,
        poolclass=__import__('sqlalchemy.pool', fromlist=['NullPool']).NullPool,
        echo=False
    )
    IsolatedSessionLocal = async_sessionmaker(isolated_engine, expire_on_commit=False)

    try:
        async with IsolatedSessionLocal() as session:
            iterations = 10
            latencies = []

            start_time = time.perf_counter()

            for i in range(iterations):
                t0 = time.perf_counter()
                await session.execute(text("SELECT 1"))
                lat = (time.perf_counter() - t0) * 1000.0
                latencies.append(lat)

            duration = time.perf_counter() - start_time
            throughput = iterations / duration if duration > 0 else 0

            latencies.sort()
            p95 = latencies[int(len(latencies) * 0.95)] if latencies else 0
            avg = sum(latencies) / len(latencies) if latencies else 0

            print("\n" + "=" * 60)
            print("Database Performance Results")
            print("=" * 60)
            print(f"  Iterations: {iterations}")
            print(f"  Duration: {duration:.3f}s")
            print(f"  Throughput: {throughput:.2f} RPS")
            print(f"  p95 Latency: {p95:.2f} ms")
            print(f"  Avg Latency: {avg:.2f} ms")
            print("=" * 60)

            assert throughput >= 1.0, f"Throughput {throughput:.2f} RPS below threshold"
            assert p95 < 500.0, f"p95 latency {p95:.2f}ms exceeds threshold"
            print("âœ… Performance test passed!")
    finally:
        await isolated_engine.dispose()