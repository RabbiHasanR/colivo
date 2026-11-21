import re
from typing import Any

import pytest
from fastapi.testclient import TestClient
from redis import Redis

from app.core.notifier import Channel
from app.modules.accounts import codes
from app.modules.accounts.constants import SESSION_COOKIE
from app.modules.accounts.contact import Contact
from tests.conftest import FakeNotifier, MovableClock

PHONE = "01712 345678"
PHONE_E164 = "+8801712345678"


@pytest.mark.xfail(
    strict=True,
    reason="acceptance: an owner signs up, which creates their home, and is logged in",
)
def test_owner_signs_up_and_home_is_created(
    client: TestClient, notifier: FakeNotifier
) -> None:
    """
    GIVEN nobody uses the phone 01712 345678
    WHEN  its owner asks for a code and signs up with it, creating "Our Flat"
    THEN  they are logged in as the owner of Our Flat, which has a Home ID
          and a setup checklist with "Home created" done
    """
    client.post("/api/v1/auth/codes", json={"contact": PHONE})
    code = notifier.last_code_to(PHONE_E164)

    sign_up = client.post(
        "/api/v1/auth/sign-up",
        json={
            "contact": PHONE,
            "code": code,
            "name": "Rabbi Hasan",
            "home_name": "Our Flat",
            "area": "Mirpur",
            "first_month": "2026-11-01",
            "lives_here": True,
        },
    )
    me = client.get("/api/v1/me").json()["data"]
    setup = client.get("/api/v1/home/setup").json()["data"]

    assert sign_up.status_code == 201
    assert me["person"]["phone"] == PHONE_E164
    assert me["membership"]["name"] == "Rabbi Hasan"
    assert me["membership"]["role"] == "owner"
    assert me["home"]["name"] == "Our Flat"
    assert re.fullmatch(r"OF-\d{4}", me["home"]["code"])
    assert {"key": "home_created", "done": True} in setup["steps"]


def sign_up_body(code: str, **changes: Any) -> dict[str, Any]:
    """The sign-up request for "Our Flat" by 01712 345678, with any field changed."""
    return {
        "contact": PHONE_E164,
        "code": code,
        "name": "Rabbi Hasan",
        "home_name": "Our Flat",
        "area": "Mirpur",
        "first_month": "2026-11-01",
        "lives_here": True,
    } | changes


def code_for_phone(redis_client: Redis, clock: MovableClock) -> str:
    """Issue a code for 01712 345678 straight from the code store."""
    contact = Contact(channel=Channel.SMS, value=PHONE_E164)
    return codes.issue_code(redis_client, contact, clock())


def test_sign_up_answers_201_with_the_new_home_and_a_session_cookie(
    client: TestClient, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN a valid code for 01712 345678
    WHEN  POST /api/v1/auth/sign-up creates "Our Flat"
    THEN  it answers 201 with the owner and the home, and sets the session cookie
    """
    code = code_for_phone(redis_client, clock)

    response = client.post("/api/v1/auth/sign-up", json=sign_up_body(code))

    assert response.status_code == 201
    data = response.json()["data"]
    assert data["membership"]["role"] == "owner"
    assert data["home"]["name"] == "Our Flat"
    assert SESSION_COOKIE in response.cookies


@pytest.mark.parametrize(
    "changes",
    [
        pytest.param({"name": None}, id="no name"),
        pytest.param({"name": "   "}, id="blank name"),
        pytest.param({"home_name": "x" * 81}, id="home name over 80"),
        pytest.param({"area": "x" * 81}, id="area over 80"),
    ],
)
def test_sign_up_answers_422_for_a_bad_name(
    client: TestClient,
    redis_client: Redis,
    clock: MovableClock,
    changes: dict[str, Any],
) -> None:
    """
    GIVEN a valid code
    WHEN  sign-up is sent with a missing, blank or too long name, home name or area
    THEN  it answers 422
    """
    code = code_for_phone(redis_client, clock)

    response = client.post("/api/v1/auth/sign-up", json=sign_up_body(code, **changes))

    assert response.status_code == 422


def test_codes_answer_the_same_for_anyone(
    client: TestClient, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN 01712 345678 owns "Our Flat", and nobody uses 01812 345678
    WHEN  POST /api/v1/auth/codes is called for each
    THEN  both answer 200 with the same body, so the answer tells nobody
          whether a number has an account
    """
    client.post(
        "/api/v1/auth/sign-up", json=sign_up_body(code_for_phone(redis_client, clock))
    )

    owner = client.post("/api/v1/auth/codes", json={"contact": PHONE_E164})
    stranger = client.post("/api/v1/auth/codes", json={"contact": "+8801812345678"})

    assert (owner.status_code, stranger.status_code) == (200, 200)
    assert owner.json() == stranger.json()


def test_codes_answer_422_for_something_that_is_not_a_phone_or_email(
    client: TestClient,
) -> None:
    """
    GIVEN the text "hello"
    WHEN  POST /api/v1/auth/codes is called with it
    THEN  it answers 422, naming the contact field
    """
    response = client.post("/api/v1/auth/codes", json={"contact": "hello"})

    assert response.status_code == 422
    assert response.json()["errors"][0].startswith("body.contact: ")


@pytest.mark.parametrize(
    ("method", "path"),
    [
        pytest.param("GET", "/api/v1/me", id="me"),
        pytest.param("POST", "/api/v1/auth/log-out", id="log-out"),
        pytest.param("GET", "/api/v1/home/setup", id="setup"),
    ],
)
@pytest.mark.parametrize(
    "cookie",
    [
        pytest.param(None, id="no cookie"),
        pytest.param(f"{SESSION_COOKIE}=not-a-session", id="unknown token"),
    ],
)
def test_endpoints_need_a_log_in(
    client: TestClient, method: str, path: str, cookie: str | None
) -> None:
    """
    GIVEN nobody is logged in, or the cookie holds a token that is no session
    WHEN  an endpoint behind log-in is called
    THEN  it answers 401
    """
    headers = {"Cookie": cookie} if cookie else {}

    response = client.request(method, path, headers=headers)

    assert response.status_code == 401


def test_log_out_ends_the_session_and_clears_the_cookie(
    client: TestClient, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN an owner who just signed up and is logged in
    WHEN  they log out
    THEN  the cookie is cleared, and their old token no longer logs anyone in
    """
    signed_up = client.post(
        "/api/v1/auth/sign-up", json=sign_up_body(code_for_phone(redis_client, clock))
    )
    token = signed_up.cookies[SESSION_COOKIE]

    response = client.post("/api/v1/auth/log-out")

    assert response.status_code == 200
    assert "Max-Age=0" in response.headers["set-cookie"]
    old_token = client.get(
        "/api/v1/me", headers={"Cookie": f"{SESSION_COOKIE}={token}"}
    )
    assert old_token.status_code == 401


def test_me_sends_the_cookie_again_for_30_days(
    client: TestClient, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN an owner who is logged in
    WHEN  the app asks who is logged in (it does on every start)
    THEN  the session cookie comes back with 30 more days, so the browser
          keeps it as long as the server does
    """
    client.post(
        "/api/v1/auth/sign-up", json=sign_up_body(code_for_phone(redis_client, clock))
    )

    response = client.get("/api/v1/me")

    assert f"{SESSION_COOKIE}=" in response.headers["set-cookie"]
    assert "Max-Age=2592000" in response.headers["set-cookie"]
