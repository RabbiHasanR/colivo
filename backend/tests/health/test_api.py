from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.database import get_session
from app.main import app


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


def test_health_answers_503_when_the_database_is_down(
    client: TestClient, unreachable_session: Session
) -> None:
    """
    GIVEN the database can't be reached and Redis is running
    WHEN  GET /api/v1/health is called
    THEN  it answers 503, still in the envelope, with success false and
          the database "down"
    """
    app.dependency_overrides[get_session] = lambda: unreachable_session

    response = client.get("/api/v1/health")

    assert response.status_code == 503
    assert response.json() == {
        "success": False,
        "message": "Service unavailable",
        "data": {"database": "down", "redis": "ok"},
    }
