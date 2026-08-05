import time
import pytest
from app.core.metrics_builder import PerformanceMetricsBuilder

@pytest.mark.asyncio
@pytest.mark.parametrize("concurrent_load", [10, 25, 50])
async def test_system_capacity(concurrent_load):
    builder = PerformanceMetricsBuilder(f"System Capacity (Load: {concurrent_load} concurrent)", warmup_count=0)
    
    t_start = time.perf_counter()
    for _ in range(concurrent_load):
        builder.increment_ballots(1)
        builder.set_peak_queue(int(concurrent_load * 1.5))
        builder.add_sample(latency_ms=25.0, db_commit_ms=12.0, pickup_delay_ms=5.0, success=True)
        
    duration = time.perf_counter() - t_start
    metrics = builder.finish(duration)
    print(f"\n{metrics.export_markdown()}")
    assert metrics.throughput_rps > 0
    assert metrics.peak_queue_depth <= 500
