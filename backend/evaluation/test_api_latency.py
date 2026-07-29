"""API latency smoke evaluation.

Measures p50 and p95 latency for login, candidate ranking, and jobs listing.
Acceptance thresholds: login p95 < 1000 ms, rank-candidates p95 < 5000 ms,
and jobs-list p95 < 500 ms. Tests are skipped when ATS_TEST_BASE_URL is not
reachable.
"""

from __future__ import annotations

import os
import statistics
import time

import httpx
import pytest


BASE_URL = os.environ.get("ATS_TEST_BASE_URL", "http://127.0.0.1:8000")


def _server_reachable():
    try:
        with httpx.Client(base_url=BASE_URL, timeout=2.0) as client:
            response = client.get("/jobs")
            return response.status_code < 500
    except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout):
        return False


SERVER_REACHABLE = _server_reachable()


def _percentiles(latencies_ms):
    sorted_values = sorted(latencies_ms)
    p50 = statistics.median(sorted_values)
    p95_index = min(len(sorted_values) - 1, int(len(sorted_values) * 0.95))
    p95 = sorted_values[p95_index]
    return p50, p95


@pytest.fixture(scope="module")
def api_client():
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        yield client


@pytest.fixture(scope="module")
def bearer_token(api_client):
    email = os.environ.get("ATS_TEST_USERNAME", "ats.eval@example.com")
    password = os.environ.get("ATS_TEST_PASSWORD", "EvalPassword123!")

    api_client.post(
        "/register",
        json={
            "full_name": "ATS Eval User",
            "email": email,
            "password": password,
        },
    )
    response = api_client.post(
        "/login",
        data={
            "username": email,
            "password": password,
        },
    )
    if response.status_code >= 400:
        pytest.skip(f"Could not obtain API token: {response.status_code} {response.text}")
    return response.json()["access_token"]


@pytest.mark.skipif(not SERVER_REACHABLE, reason=f"ATS server not reachable at {BASE_URL}")
class TestAPILatency:
    def test_login_latency(self, api_client):
        email = os.environ.get("ATS_TEST_USERNAME", "ats.eval@example.com")
        password = os.environ.get("ATS_TEST_PASSWORD", "EvalPassword123!")
        latencies = []
        for _ in range(10):
            start = time.perf_counter()
            response = api_client.post(
                "/login",
                data={
                    "username": email,
                    "password": password,
                },
            )
            latencies.append((time.perf_counter() - start) * 1000)
            assert response.status_code < 500

        p50, p95 = _percentiles(latencies)
        print(f"login p50={p50:.1f}ms p95={p95:.1f}ms")
        assert p95 < 1000

    def test_rank_candidates_latency(self, api_client, bearer_token):
        jd = (
            "We need a senior Python backend engineer with FastAPI, PostgreSQL, "
            "Docker, Redis, REST API design, production monitoring, SQL tuning, "
            "Linux debugging, async processing, code review, distributed system "
            "reliability, and experience supporting recruiter workflow products "
            "at scale while partnering with product and infrastructure teams."
        )
        headers = {"Authorization": f"Bearer {bearer_token}"}
        latencies = []
        for _ in range(5):
            start = time.perf_counter()
            response = api_client.post(
                "/rank-candidates",
                json={
                    "job_description": jd,
                    "top_k": 10,
                },
                headers=headers,
            )
            latencies.append((time.perf_counter() - start) * 1000)
            assert response.status_code < 500

        p50, p95 = _percentiles(latencies)
        print(f"rank-candidates p50={p50:.1f}ms p95={p95:.1f}ms")
        assert p95 < 5000

    def test_jobs_list_latency(self, api_client):
        latencies = []
        for _ in range(10):
            start = time.perf_counter()
            response = api_client.get("/jobs")
            latencies.append((time.perf_counter() - start) * 1000)
            assert response.status_code < 500

        p50, p95 = _percentiles(latencies)
        print(f"jobs p50={p50:.1f}ms p95={p95:.1f}ms")
        assert p95 < 500
