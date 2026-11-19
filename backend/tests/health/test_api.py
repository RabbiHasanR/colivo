import pytest
from fastapi.testclient import TestClient


@pytest.mark.xfail(
    strict=True,
    reason="acceptance: the health check reports the database and Redis",
)
def test_health_reports_database_and_redis_ok(client: TestClient) -> None:
    """
    GIVEN PostgreSQL and Redis are running (docker compose)
    WHEN  GET /api/v1/health is called
    THEN  it answers 200 with both "ok", inside the standard envelope
    """
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "Healthy",
        "data": {"database": "ok", "redis": "ok"},
    }
