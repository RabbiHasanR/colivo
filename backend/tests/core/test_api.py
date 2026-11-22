import json

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.core.config import settings
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


class PetIn(BaseModel):
    """A throwaway request body for the 422 test."""

    name: str
    age: int


def test_invalid_input_answers_422_in_the_envelope() -> None:
    """
    GIVEN an endpoint whose body needs a name and an age
    WHEN  it is called with no name and an age that isn't a number
    THEN  it answers 422 in the envelope, one "<location>: <message>" string
          per problem
    """
    app = create_app()

    @app.post("/api/v1/pets")
    def add_pet(pet: PetIn) -> None:
        """Accept a pet."""

    client = TestClient(app)

    response = client.post("/api/v1/pets", json={"age": "old"})

    assert response.status_code == 422
    assert response.json() == {
        "success": False,
        "message": "Validation Error",
        "errors": [
            "body.name: Field required",
            "body.age: Input should be a valid integer, "
            "unable to parse string as an integer",
        ],
    }


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


WEB_ORIGIN = "https://web.colivo.example"


@pytest.mark.parametrize(
    ("origin", "allowed"),
    [
        pytest.param(WEB_ORIGIN, True, id="web origin"),
        pytest.param("https://other.example", False, id="other origin"),
    ],
)
def test_only_the_web_origin_gets_cors_permission(
    origin: str, allowed: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    GIVEN BACKEND_CORS_ORIGINS lists only the web app's origin
    WHEN  a browser asks (preflight) whether a page on `origin` may call the API
    THEN  only the web origin is allowed
    """
    monkeypatch.setattr(settings, "backend_cors_origins", [WEB_ORIGIN])
    client = TestClient(create_app())

    response = client.options(
        "/api/v1/health",
        headers={"Origin": origin, "Access-Control-Request-Method": "GET"},
    )

    expected = origin if allowed else None
    assert response.headers.get("access-control-allow-origin") == expected


@pytest.mark.parametrize(
    ("origin", "expected"),
    [
        pytest.param(
            WEB_ORIGIN,
            {
                "status": 200,
                "access-control-allow-origin": WEB_ORIGIN,
                "access-control-allow-credentials": "true",
            },
            id="web origin",
        ),
        pytest.param(
            "https://other.example",
            {"status": 400, "access-control-allow-origin": None},
            id="other origin",
        ),
    ],
)
def test_only_the_web_origin_may_send_credentials(
    origin: str, expected: dict[str, object], monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    GIVEN BACKEND_CORS_ORIGINS lists only the web app's origin
    WHEN  a browser asks (pre-flight) whether a page on `origin` may POST with
          its cookies and a JSON body
    THEN  the web origin may, with credentials; another origin is refused
          (400, no allowed origin), so the browser never sends its request
    """
    monkeypatch.setattr(settings, "backend_cors_origins", [WEB_ORIGIN])
    client = TestClient(create_app())

    response = client.options(
        "/api/v1/auth/log-out",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    actual = {"status": response.status_code} | {
        name: response.headers.get(name) for name in expected if name != "status"
    }
    assert actual == expected
