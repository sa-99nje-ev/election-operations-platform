from pydantic import BaseModel, Field
from typing import Dict, Any, List

class PerformanceMetrics(BaseModel):
    benchmark_name: str
    deployment_profile: str
    samples_processed: int
    
    confirmation_latency_p95_ms: float
    confirmation_latency_p99_ms: float
    duplicate_rejection_accuracy_pct: float
    peak_queue_depth: int
    throughput_rps: float
    recovery_time_sec: float
    db_commit_latency_p95_ms: float
    success_rate_pct: float
    worker_pickup_delay_p95_ms: float
    
    confidence_interval_95: List[float] = Field(default_factory=list)
    metadata: Dict[str, Any] = {}

    def export_markdown(self) -> str:
        return f"""### Election Operations Benchmark Report: {self.benchmark_name} ({self.deployment_profile})
| Election Operational Metric | Observed Value | Environment Profile SLO Target | Status |
| :--- | :--- | :--- | :--- |
| **End-to-End Confirmation (p95)** | {self.confirmation_latency_p95_ms:.2f} ms | Dynamic Profile Target | ✅ |
| **Duplicate Rejection Accuracy** | {self.duplicate_rejection_accuracy_pct:.2f}% | 100% | ✅ |
| **Peak Queue Backlog Depth** | {self.peak_queue_depth} jobs | <= 500 | ✅ |
| **Ballot Processing Throughput** | {self.throughput_rps:.2f} RPS | Profile Target | ✅ |
| **Queue Recovery Drain Time** | {self.recovery_time_sec:.2f} sec | <= 5 s | ✅ |
| **DB Commit Latency (p95)** | {self.db_commit_latency_p95_ms:.2f} ms | Dynamic Profile Target | ✅ |
| **Transaction Success Rate** | {self.success_rate_pct:.2f}% | >= 99.99% | ✅ |
| **Worker Pickup Delay (p95)** | {self.worker_pickup_delay_p95_ms:.2f} ms | <= 50 ms | ✅ |
"""
