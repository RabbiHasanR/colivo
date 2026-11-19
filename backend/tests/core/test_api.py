from fastapi.testclient import TestClient


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
