import json

from fastapi.testclient import TestClient

from app.main import create_app


def test_unknown_path_answers_404_in_the_envelope(client: TestClient) -> None:
    """
    GIVEN no endpoint at /api/v1/nothing-here
    WHEN  it is called
    THEN  it answers 404 inside the standard envelope
    """
    response = client.get("/api/v1/nothing-here")

    assert response.status_code == 404
    assert response.json() == {
        "success": False,
        "message": "Not Found",
        "errors": ["Not Found"],
    }


def test_unexpected_error_answers_500_without_internals() -> None:
    """
    GIVEN an endpoint that fails with an unexpected error carrying internals
    WHEN  it is called
    THEN  it answers 500 in the envelope with a generic message, and nothing
          from the error reaches the client
    """
    app = create_app()

    @app.get("/api/v1/boom")
    def boom() -> None:
        raise RuntimeError("db password=hunter2 at 10.0.0.5")

    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/api/v1/boom")

    assert response.status_code == 500
    assert response.json() == {
        "success": False,
        "message": "Internal Server Error",
        "errors": ["An unexpected error occurred."],
    }
    assert "hunter2" not in response.text


def test_openapi_describes_health_inside_the_envelope(client: TestClient) -> None:
    """
    GIVEN the published API contract (/openapi.json)
    WHEN  the health check's 200 and 503 responses are read
    THEN  both are the StandardResponse envelope, with HealthOut as its data
    """
    spec = client.get("/openapi.json").json()
    responses = spec["paths"]["/api/v1/health"]["get"]["responses"]

    for status in ("200", "503"):
        ref = responses[status]["content"]["application/json"]["schema"]["$ref"]
        schema = spec["components"]["schemas"][
            ref.removeprefix("#/components/schemas/")
        ]

        assert set(schema["properties"]) == {"success", "message", "data", "errors"}, (
            status
        )
        assert "#/components/schemas/HealthOut" in json.dumps(
            schema["properties"]["data"]
        ), status
