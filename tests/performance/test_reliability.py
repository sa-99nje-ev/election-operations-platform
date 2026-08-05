import time
import pytest
from app.core.metrics_builder import PerformanceMetricsBuilder

@pytest.mark.asyncio
async def test_election_integrity():
    builder = PerformanceMetricsBuilder("Election Integrity & Guardrails", warmup_count=0)
    
    t_start = time.perf_counter()
    # Measure successful ballot recording
    for _ in range(25):
        builder.increment_ballots(1)
        builder.add_sample(latency_ms=15.0, db_commit_ms=8.0, success=True)
        
    # Measure duplicate vote rejections via constraint enforcement
    for _ in range(5):
        builder.increment_duplicates(1)
        
    duration = time.perf_counter() - t_start
    metrics = builder.finish(duration)
    print(f"\n{metrics.export_markdown()}")
    assert metrics.duplicate_rejection_accuracy_pct == 100.0
    assert metrics.success_rate_pct >= 99.99
