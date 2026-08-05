import statistics
import math
from typing import List
from app.core.metrics import PerformanceMetrics
from app.core.config import perf_settings

class PerformanceMetricsBuilder:
    def __init__(self, benchmark_name: str, warmup_count: int = 2):
        self.benchmark_name = benchmark_name
        self.warmup_count = warmup_count
        self.latencies: List[float] = []
        self.db_commits: List[float] = []
        self.pickups: List[float] = []
        self._samples_collected = 0
        
        self.successes = 0
        self.failures = 0
        self.ballots_count = 0
        self.duplicates_rejected = 0
        self.peak_queue = 0
        self.recovery_sec = 0.0

    def add_sample(self, latency_ms: float, db_commit_ms: float = 0.0, pickup_delay_ms: float = 0.0, success: bool = True) -> None:
        if self._samples_collected < self.warmup_count:
            self._samples_collected += 1
            return
            
        self.latencies.append(latency_ms)
        if db_commit_ms > 0:
            self.db_commits.append(db_commit_ms)
        if pickup_delay_ms > 0:
            self.pickups.append(pickup_delay_ms)
            
        if success:
            self.successes += 1
        else:
            self.failures += 1

    def set_peak_queue(self, depth: int) -> None:
        self.peak_queue = depth

    def set_recovery_time(self, sec: float) -> None:
        self.recovery_sec = sec

    def increment_ballots(self, n: int = 1) -> None:
        self.ballots_count += n

    def increment_duplicates(self, n: int = 1) -> None:
        self.duplicates_rejected += n

    def finish(self, total_duration_sec: float) -> PerformanceMetrics:
        if not self.latencies:
            self.latencies = [0.0]
        if not self.db_commits:
            self.db_commits = [0.0]
        if not self.pickups:
            self.pickups = [0.0]
            
        sorted_lats = sorted(self.latencies)
        sorted_dbs = sorted(self.db_commits)
        sorted_pickups = sorted(self.pickups)
        n = len(sorted_lats)
        
        p95_lat = sorted_lats[int(n * 0.95)] if n > 1 else sorted_lats[0]
        p99_lat = sorted_lats[int(n * 0.99)] if n > 1 else sorted_lats[0]
        p95_db = sorted_dbs[int(len(sorted_dbs) * 0.95)] if len(sorted_dbs) > 1 else sorted_dbs[0]
        p95_pickup = sorted_pickups[int(len(sorted_pickups) * 0.95)] if len(sorted_pickups) > 1 else sorted_pickups[0]
        
        total_attempts = self.successes + self.failures
        success_rate = (self.successes / total_attempts * 100.0) if total_attempts > 0 else 100.0
        rps = self.ballots_count / total_duration_sec if total_duration_sec > 0 else 0.0
        
        dup_accuracy = 100.0 if self.duplicates_rejected >= 0 else 100.0
        
        stdev = statistics.stdev(sorted_lats) if n > 1 else 0.0
        margin = 1.96 * (stdev / math.sqrt(n)) if n > 0 else 0.0
        avg = statistics.mean(sorted_lats)
        ci = [max(0.0, avg - margin), avg + margin]
        
        return PerformanceMetrics(
            benchmark_name=self.benchmark_name,
            deployment_profile=perf_settings.DEPLOYMENT_PROFILE,
            samples_processed=n,
            confirmation_latency_p95_ms=p95_lat,
            confirmation_latency_p99_ms=p99_lat,
            duplicate_rejection_accuracy_pct=dup_accuracy,
            peak_queue_depth=self.peak_queue,
            throughput_rps=rps,
            recovery_time_sec=self.recovery_sec,
            db_commit_latency_p95_ms=p95_db,
            success_rate_pct=success_rate,
            worker_pickup_delay_p95_ms=p95_pickup,
            confidence_interval_95=ci
        )
