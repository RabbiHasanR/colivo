import re
from datetime import timedelta
from typing import Any

import pytest
from fastapi.testclient import TestClient
from redis import Redis

from app.core.config import settings
from app.core.notifier import Channel
from app.modules.accounts import codes
from app.modules.accounts.constants import SESSION_COOKIE
from app.modules.accounts.contact import Contact
from tests.conftest import FakeNotifier, MovableClock

PHONE = "01712 345678"
PHONE_E164 = "+8801712345678"


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
    # A new code waits a minute after the last one (B11).
    clock.advance(timedelta(minutes=2))

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


@pytest.mark.parametrize("secure", [True, False], ids=["secure on", "secure off"])
def test_session_cookie_is_httponly_lax_and_secure_when_set(
    client: TestClient,
    redis_client: Redis,
    clock: MovableClock,
    monkeypatch: pytest.MonkeyPatch,
    secure: bool,
) -> None:
    """
    GIVEN SESSION_COOKIE_SECURE is on (any real deployment) or off (localhost)
    WHEN  someone signs up and gets the session cookie
    THEN  page scripts can't read it (HttpOnly), other sites can't send it on
          their forms (SameSite=Lax), and it travels over HTTPS only when on
    """
    monkeypatch.setattr(settings, "session_cookie_secure", secure)

    response = client.post(
        "/api/v1/auth/sign-up", json=sign_up_body(code_for_phone(redis_client, clock))
    )

    attributes = {
        part.strip().split("=")[0].lower()
        for part in response.headers["set-cookie"].split(";")
    }
    assert {"httponly", "samesite"} <= attributes
    assert "samesite=lax" in response.headers["set-cookie"].lower()
    assert ("secure" in attributes) == secure


def test_owner_logs_back_in_with_one_time_code(
    client: TestClient, redis_client: Redis, notifier: FakeNotifier, clock: MovableClock
) -> None:
    """
    GIVEN the owner of "Our Flat" signed up and then logged out
    WHEN  two minutes later they ask for a code and log in with it
    THEN  they are logged in again as the owner of Our Flat
    """
    client.post(
        "/api/v1/auth/sign-up", json=sign_up_body(code_for_phone(redis_client, clock))
    )
    client.post("/api/v1/auth/log-out")
    clock.advance(timedelta(minutes=2))

    client.post("/api/v1/auth/codes", json={"contact": PHONE})
    logged_in = client.post(
        "/api/v1/auth/log-in",
        json={"contact": PHONE, "code": notifier.last_code_to(PHONE_E164)},
    )
    me = client.get("/api/v1/me").json()["data"]

    assert logged_in.status_code == 200
    assert (me["membership"]["role"], me["home"]["name"]) == ("owner", "Our Flat")


def test_log_in_answers_422_for_something_that_is_not_a_phone_or_email(
    client: TestClient,
) -> None:
    """
    GIVEN the text "hello"
    WHEN  POST /api/v1/auth/log-in is called with it and a code
    THEN  it answers 422, naming the contact field
    """
    response = client.post(
        "/api/v1/auth/log-in", json={"contact": "hello", "code": "123456"}
    )

    assert response.status_code == 422
    assert response.json()["errors"][0].startswith("body.contact: ")


def test_log_in_with_an_expired_code_answers_400_with_the_reason(
    client: TestClient, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN a code sent to 01712 345678 five minutes ago
    WHEN  POST /api/v1/auth/log-in uses it
    THEN  it answers 400, and the envelope's data says the code expired
    """
    code = code_for_phone(redis_client, clock)
    clock.advance(timedelta(minutes=5))

    response = client.post(
        "/api/v1/auth/log-in", json={"contact": PHONE_E164, "code": code}
    )

    assert response.status_code == 400
    assert response.json() == {
        "success": False,
        "message": "This code expired. Codes work for 5 minutes.",
        "errors": ["This code expired. Codes work for 5 minutes."],
        "data": {"reason": "expired"},
    }


def test_log_in_with_a_wrong_code_answers_400_with_tries_left(
    client: TestClient, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN a code sent to 01712 345678
    WHEN  POST /api/v1/auth/log-in is sent with a different code
    THEN  it answers 400, and the envelope's data says how many tries are left
    """
    code = code_for_phone(redis_client, clock)
    wrong = f"{(int(code) + 1) % 1_000_000:06d}"

    response = client.post(
        "/api/v1/auth/log-in", json={"contact": PHONE_E164, "code": wrong}
    )

    assert response.status_code == 400
    assert response.json()["data"] == {"reason": "wrong", "tries_left": 4}


def test_codes_say_when_the_next_one_can_be_sent(client: TestClient) -> None:
    """
    GIVEN nobody has asked for a code for 01712 345678 yet
    WHEN  POST /api/v1/auth/codes is called, and again at once
    THEN  the first answer says a new code can be sent in 60 seconds; the
          second is refused with 429 and the same 60 seconds to wait
    """
    first = client.post("/api/v1/auth/codes", json={"contact": PHONE})
    again = client.post("/api/v1/auth/codes", json={"contact": PHONE})

    assert first.json()["data"]["resend_in_seconds"] == 60
    assert again.status_code == 429
    assert again.json()["data"] == {"reason": "too_soon", "retry_in_seconds": 60}


MARUF_PHONE = "01812 345678"
MARUF_E164 = "+8801812345678"


@pytest.mark.xfail(
    strict=True,
    reason="acceptance: the owner adds a member, who can then log in",
)
def test_owner_adds_member_who_then_logs_in(
    client: TestClient, redis_client: Redis, notifier: FakeNotifier, clock: MovableClock
) -> None:
    """
    GIVEN Rabbi Hasan owns "Our Flat"
    WHEN  he adds Maruf by phone, and Maruf logs in with a one-time code
    THEN  Maruf got a notice, and is logged in as a member of Our Flat added
          by Rabbi Hasan
    """
    client.post(
        "/api/v1/auth/sign-up", json=sign_up_body(code_for_phone(redis_client, clock))
    )

    added = client.post(
        "/api/v1/members",
        json={
            "name": "Maruf",
            "contact": MARUF_PHONE,
            "joined_on": "2026-11-21",
            "role": "member",
        },
    )
    client.post("/api/v1/auth/log-out")
    client.post("/api/v1/auth/codes", json={"contact": MARUF_PHONE})
    client.post(
        "/api/v1/auth/log-in",
        json={"contact": MARUF_PHONE, "code": notifier.last_code_to(MARUF_E164)},
    )
    me = client.get("/api/v1/me").json()["data"]

    assert added.status_code == 201
    assert any(
        message.to == MARUF_E164 and "Our Flat" in message.text
        for message in notifier.sent
    ), "Maruf was told he was added"
    assert (me["membership"]["name"], me["membership"]["role"]) == ("Maruf", "member")
    assert me["home"]["name"] == "Our Flat"
    assert me["membership"]["added_by_name"] == "Rabbi Hasan"


def maruf_body(**changes: Any) -> dict[str, Any]:
    """Adding Maruf (01812 345678) as a member from 21 Nov 2026, with changes."""
    return {
        "name": "Maruf",
        "contact": MARUF_PHONE,
        "joined_on": "2026-11-21",
        "role": "member",
    } | changes


def sign_up_owner(client: TestClient, redis_client: Redis, clock: MovableClock) -> None:
    """Sign Rabbi Hasan up as the owner of "Our Flat"; the client is logged in."""
    client.post(
        "/api/v1/auth/sign-up", json=sign_up_body(code_for_phone(redis_client, clock))
    )


@pytest.mark.parametrize(
    "changes",
    [
        pytest.param({"name": "  "}, id="blank name"),
        pytest.param({"contact": "hello"}, id="not a phone or email"),
    ],
)
def test_add_member_answers_422_for_a_bad_name_or_contact(
    client: TestClient,
    redis_client: Redis,
    clock: MovableClock,
    changes: dict[str, Any],
) -> None:
    """
    GIVEN the owner of "Our Flat" is logged in
    WHEN  POST /api/v1/members is sent with a blank name or a contact that is
          neither a phone nor an email
    THEN  it answers 422
    """
    sign_up_owner(client, redis_client, clock)

    response = client.post("/api/v1/members", json=maruf_body(**changes))

    assert response.status_code == 422
