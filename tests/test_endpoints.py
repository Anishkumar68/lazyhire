import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_openapi_schema(async_client: AsyncClient):
    response = await async_client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "paths" in schema
    paths = schema["paths"]

    # Verify key endpoint groups are present
    assert "/api/v1/jobs/scrape" in paths
    assert "/api/v1/jobs/ingest" in paths
    assert "/api/v1/jobs/{job_id}/fit-score" in paths
    assert "/api/v1/profiles/{candidate_id}/stories" in paths
    assert "/api/v1/materials/tailor/resume" in paths
    assert "/api/v1/materials/tailor/cover-letter" in paths
    assert "/api/v1/review/{application_id}/preview" in paths
    assert "/api/v1/execution/start" in paths
    assert "/api/v1/execution/status" in paths
    assert "/api/v1/execution/solve-question" in paths
    assert "/api/v1/tasks/queues" in paths
    assert "/api/v1/tasks/dlq" in paths
    assert "/api/v1/analytics/dashboard" in paths
    assert "/api/v1/analytics/tokens" in paths
    assert "/api/v1/providers/supported" in paths


@pytest.mark.asyncio
async def test_pass_endpoints_callable(async_client: AsyncClient):
    # Test execution status endpoint (stubbed with pass)
    res_status = await async_client.get("/api/v1/execution/status")
    assert res_status.status_code == 200

    # Test tasks queues endpoint (stubbed with pass)
    res_queues = await async_client.get("/api/v1/tasks/queues")
    assert res_queues.status_code == 200

    # Test analytics dashboard endpoint (stubbed with pass)
    res_analytics = await async_client.get("/api/v1/analytics/dashboard")
    assert res_analytics.status_code == 200
