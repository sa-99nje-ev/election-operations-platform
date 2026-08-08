"""
Locust load testing script to simulate high-concurrency voting load
against FastAPI + ARQ.
"""

import random
import uuid

from locust import HttpUser, between, events, task


class VoterUser(HttpUser):
    wait_time = between(0.1, 0.5)

    def on_start(self):
        """Initialize user session."""
        self.headers = {
            "Content-Type": "application/json",
        }

        # Realistic test data
        self.candidate_id = "123e4567-e89b-12d3-a456-426614174001"
        self.booth_id = "123e4567-e89b-12d3-a456-426614174002"

    @task(5)
    def cast_vote(self):
        """Cast a vote - primary task."""
        payload = {
            "voter_id": str(uuid.uuid4()),
            "candidate_id": self.candidate_id,
            "booth_id": self.booth_id,
            "ip_address": (
                f"192.168.{random.randint(1, 255)}."
                f"{random.randint(1, 255)}"
            ),
            "trace_id": str(uuid.uuid4()),
        }

        with self.client.post(
            "/vote",
            json=payload,
            headers=self.headers,
            catch_response=True,
            name="POST /vote",
        ) as response:
            if response.status_code == 202:
                response.success()
            else:
                response.failure(
                    f"Status {response.status_code}: {response.text}"
                )

    @task(2)
    def health_check(self):
        """Health check - secondary task."""
        with self.client.get(
            "/health",
            catch_response=True,
            name="GET /health",
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Health check failed: {response.status_code}"
                )

    @task(1)
    def get_results(self):
        """Get results - tertiary task."""
        with self.client.get(
            "/results",
            catch_response=True,
            name="GET /results",
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Results request failed: {response.status_code}"
                )


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Print load-test configuration when the test starts."""
    print("=" * 60)
    print("🚀 Starting Election Platform Load Test")
    print("=" * 60)
    print(f"Target: {environment.host}")
    print(f"User Class: {VoterUser.__name__}")
    print("=" * 60)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Print aggregate load-test statistics when the test stops."""
    print("\n" + "=" * 60)
    print("📊 Load Test Complete")
    print("=" * 60)

    stats = environment.runner.stats
    total_requests = stats.total.num_requests
    total_failures = stats.total.num_failures

    print(f"Total Requests: {total_requests}")
    print(f"Total Failures: {total_failures}")

    if total_requests > 0:
        failure_rate = (total_failures / total_requests) * 100
        print(f"Failure Rate: {failure_rate:.2f}%")

    print("=" * 60)