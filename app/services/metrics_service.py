"""
Metrics aggregation service for system component health and queue stats.
"""

import time
from typing import Dict, Any
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.queue.queue_service import QueueService
from app.celery_app import celery


class MetricsService:
    """Consolidated metrics service for API, Database, Redis, and Celery."""

    def __init__(self, session: Session, queue_service: QueueService):
        self.session = session
        self.queue_service = queue_service

    def get_database_metrics(self) -> Dict[str, Any]:
        """Check database ping and connectivity latency."""
        start = time.time()
        try:
            self.session.execute(text("SELECT 1"))
            latency = round((time.time() - start) * 1000, 2)
            return {"status": "healthy", "latency_ms": latency}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def get_redis_metrics(self) -> Dict[str, Any]:
        """Check Redis connectivity and fetch queue lengths."""
        healthy = self.queue_service.is_healthy()
        stats = self.queue_service.get_queue_stats()
        return {
            "status": "healthy" if healthy else "unhealthy",
            "stats": stats
        }

    def get_celery_metrics(self) -> Dict[str, Any]:
        """Inspect Celery workers status via control ping."""
        try:
            inspect = celery.control.inspect()
            ping_res = inspect.ping()
            active_workers = len(ping_res) if ping_res else 0
            return {
                "status": "healthy" if active_workers > 0 else "degraded",
                "active_workers": active_workers
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def get_all_metrics(self) -> Dict[str, Any]:
        """Aggregate health and operational metrics for all platform layers."""
        return {
            "database": self.get_database_metrics(),
            "redis": self.get_redis_metrics(),
            "celery": self.get_celery_metrics()
        }