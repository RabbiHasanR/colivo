import re
import uuid
from datetime import date, timedelta
from typing import Any

import pytest
from fastapi.testclient import TestClient
from redis import Redis
from sqlmodel import Session, func, select

from app.core.config import settings
from app.core.notifier import Channel
from app.modules.accounts import codes, sessions
from app.modules.accounts.constants import HOME_HEADER, SESSION_COOKIE
from app.modules.accounts.contact import Contact
from app.modules.accounts.models import (
    Membership,
    MembershipPeriod,
    MembershipStatus,
    Person,
    Role,
)
from app.modules.homes import service as homes_service
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


def owner_home_id(client: TestClient) -> uuid.UUID:
    """The logged-in person's home."""
    return uuid.UUID(client.get("/api/v1/me").json()["data"]["home"]["id"])


def log_in_as_new(
    client: TestClient,
    session: Session,
    redis_client: Redis,
    clock: MovableClock,
    *,
    role: Role,
    phone: str = "+8801912345678",
) -> None:
    """Put someone with ``role`` in the logged-in person's home, and log in as them.

    Set-up only: members can't be given roles through the API until group 5.
    """
    home_id = owner_home_id(client)
    person = Person(phone=phone)
    session.add(person)
    session.flush()
    session.add(
        Membership(home_id=home_id, person_id=person.id, name="Hijam", role=role)
    )
    session.flush()
    token = sessions.create_session(redis_client, person.id, clock())
    client.cookies.clear()
    client.cookies.set(SESSION_COOKIE, token)


def members_named(session: Session, name: str) -> int:
    """How many memberships have ``name``."""
    return session.exec(
        select(func.count()).select_from(Membership).where(Membership.name == name)
    ).one()


@pytest.mark.parametrize(
    ("adder", "status", "added"),
    [
        pytest.param(Role.OWNER, 201, 1, id="owner"),
        pytest.param(Role.MANAGER, 403, 0, id="manager"),
    ],
)
def test_only_the_owner_can_add_a_manager(
    client: TestClient,
    session: Session,
    redis_client: Redis,
    clock: MovableClock,
    adder: Role,
    status: int,
    added: int,
) -> None:
    """
    GIVEN "Our Flat", with its owner and (in one case) a manager logged in
    WHEN  they add Maruf as a manager
    THEN  the owner may (201); a manager may not (403), and nobody is added
    """
    sign_up_owner(client, redis_client, clock)
    if adder == Role.MANAGER:
        log_in_as_new(client, session, redis_client, clock, role=Role.MANAGER)

    response = client.post("/api/v1/members", json=maruf_body(role="manager"))

    assert (response.status_code, members_named(session, "Maruf")) == (status, added)


@pytest.mark.parametrize(
    ("method", "body"),
    [
        pytest.param("GET", None, id="see the list"),
        pytest.param("POST", maruf_body(), id="add a member"),
    ],
)
def test_members_answer_403_for_a_member(
    client: TestClient,
    session: Session,
    redis_client: Redis,
    clock: MovableClock,
    method: str,
    body: dict[str, Any] | None,
) -> None:
    """
    GIVEN a member (not the owner or a manager) of "Our Flat" is logged in
    WHEN  they ask for the members list, or try to add a member
    THEN  both answer 403
    """
    sign_up_owner(client, redis_client, clock)
    log_in_as_new(client, session, redis_client, clock, role=Role.MEMBER)

    response = client.request(method, "/api/v1/members", json=body)

    assert response.status_code == 403


def test_change_member_answers_422_for_a_blank_name(
    client: TestClient, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN the owner of "Our Flat" added Maruf
    WHEN  PATCH /api/v1/members/<Maruf> sends a blank name
    THEN  it answers 422
    """
    sign_up_owner(client, redis_client, clock)
    member_id = client.post("/api/v1/members", json=maruf_body()).json()["data"]["id"]

    response = client.patch(f"/api/v1/members/{member_id}", json={"name": "  "})

    assert response.status_code == 422


def test_change_me_answers_422_for_a_blank_name(
    client: TestClient, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN the owner of "Our Flat" is logged in
    WHEN  PATCH /api/v1/me sends a blank name
    THEN  it answers 422
    """
    sign_up_owner(client, redis_client, clock)

    response = client.patch("/api/v1/me", json={"name": "  "})

    assert response.status_code == 422


def member_of_old_fort(session: Session) -> Membership:
    """Karim, a member of another home, "Old Fort"."""
    home = homes_service.create_home(
        session, name="Old Fort", area="Dhanmondi", first_month=date(2026, 1, 1)
    )
    person = Person(phone="+8801612345678")
    session.add(person)
    session.flush()
    karim = Membership(home_id=home.id, person_id=person.id, name="Karim")
    session.add(karim)
    session.flush()
    return karim


@pytest.mark.parametrize("whose", ["another home's", "nobody's"])
def test_changing_another_homes_member_answers_404(
    client: TestClient,
    session: Session,
    redis_client: Redis,
    clock: MovableClock,
    whose: str,
) -> None:
    """
    GIVEN the owner of "Our Flat" is logged in, and Karim is in "Old Fort"
    WHEN  they try to rename Karim, or a member id that doesn't exist
    THEN  it answers 404, and nothing about Old Fort is in the answer
    """
    sign_up_owner(client, redis_client, clock)
    karim = member_of_old_fort(session)
    member_id = karim.id if whose == "another home's" else uuid.uuid7()

    response = client.patch(f"/api/v1/members/{member_id}", json={"name": "Rahim"})

    assert response.status_code == 404
    assert "Karim" not in response.text and "Old Fort" not in response.text
    session.refresh(karim)
    assert karim.name == "Karim"


def test_member_of_another_home_is_added_to_this_home(
    client: TestClient, session: Session, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN Karim is an active member of "Old Fort", and Rabbi owns "Our Flat"
    WHEN  Rabbi adds Karim's phone to Our Flat
    THEN  Karim is a member of Our Flat too, and still active in Old Fort
    """
    sign_up_owner(client, redis_client, clock)
    karim = member_of_old_fort(session)

    response = client.post(
        "/api/v1/members", json=maruf_body(name="Karim", contact="01612 345678")
    )

    assert response.status_code == 201
    names = [m["name"] for m in client.get("/api/v1/members").json()["data"]]
    assert "Karim" in names
    session.refresh(karim)
    assert karim.status == "active"


def test_person_in_two_homes_shows_each_homes_details_only(
    client: TestClient, session: Session, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN Maruf is "Maruf Ahmed", a manager of "Old Fort" since January
    WHEN  the owner of "Our Flat" adds him as "Maruf", a member from 21 Nov,
          and asks for the members list
    THEN  Our Flat lists him as "Maruf", member, joined 21 Nov, and nothing of
          his Old Fort name, role, dates or home
    """
    sign_up_owner(client, redis_client, clock)
    old_fort = homes_service.create_home(
        session, name="Old Fort", area=None, first_month=date(2026, 1, 1)
    )
    person = Person(phone=MARUF_E164)
    session.add(person)
    session.flush()
    in_old_fort = Membership(
        home_id=old_fort.id, person_id=person.id, name="Maruf Ahmed", role=Role.MANAGER
    )
    session.add(in_old_fort)
    session.flush()
    session.add(
        MembershipPeriod(
            home_id=old_fort.id,
            membership_id=in_old_fort.id,
            starts_on=date(2026, 1, 1),
        )
    )
    session.flush()
    client.post("/api/v1/members", json=maruf_body())

    response = client.get("/api/v1/members")

    [maruf] = [m for m in response.json()["data"] if m["phone"] == MARUF_E164]
    assert (maruf["name"], maruf["role"], maruf["joined_on"]) == (
        "Maruf",
        "member",
        "2026-11-21",
    )
    for other in ("Maruf Ahmed", "manager", "Old Fort", "2026-01-01"):
        assert other not in response.text


def test_members_list_shows_only_this_homes_members(
    client: TestClient, session: Session, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN "Our Flat" has its owner and Maruf, and Karim is in "Old Fort"
    WHEN  the owner of Our Flat asks for the members list
    THEN  it lists Maruf and the owner, and nothing of Old Fort
    """
    sign_up_owner(client, redis_client, clock)
    client.post("/api/v1/members", json=maruf_body())
    member_of_old_fort(session)

    response = client.get("/api/v1/members")

    names = [member["name"] for member in response.json()["data"]]
    assert names == ["Maruf", "Rabbi Hasan"]
    assert "Old Fort" not in response.text


def test_owner_deactivates_member_who_can_no_longer_log_in(
    client: TestClient, redis_client: Redis, notifier: FakeNotifier, clock: MovableClock
) -> None:
    """
    GIVEN Rabbi Hasan owns "Our Flat" and added Maruf, joining 21 Nov 2026
    WHEN  he deactivates Maruf from today, and Maruf then tries to log in
    THEN  Maruf is inactive, and his log-in, with the right code, answers 404
          "Not added yet"
    """
    sign_up_owner(client, redis_client, clock)
    member_id = client.post("/api/v1/members", json=maruf_body()).json()["data"]["id"]

    deactivated = client.post(
        f"/api/v1/members/{member_id}/deactivate", json={"on": "2026-11-21"}
    )
    client.post("/api/v1/auth/log-out")
    client.post("/api/v1/auth/codes", json={"contact": MARUF_PHONE})
    log_in = client.post(
        "/api/v1/auth/log-in",
        json={"contact": MARUF_PHONE, "code": notifier.last_code_to(MARUF_E164)},
    )

    assert deactivated.status_code == 200
    assert deactivated.json()["data"]["status"] == "inactive"
    assert log_in.status_code == 404


def add_maruf(client: TestClient) -> str:
    """The logged-in owner adds Maruf; returns his member id."""
    return client.post("/api/v1/members", json=maruf_body()).json()["data"]["id"]


@pytest.mark.parametrize("caller", [Role.MANAGER, Role.MEMBER])
def test_only_the_owner_changes_roles(
    client: TestClient,
    session: Session,
    redis_client: Redis,
    clock: MovableClock,
    caller: Role,
) -> None:
    """
    GIVEN "Our Flat" with Maruf, and a manager (or member) logged in
    WHEN  they try to make Maruf a manager
    THEN  it answers 403: only the owner gives roles (FR-63)
    """
    sign_up_owner(client, redis_client, clock)
    member_id = add_maruf(client)
    log_in_as_new(client, session, redis_client, clock, role=caller)

    response = client.put(f"/api/v1/members/{member_id}/role", json={"role": "manager"})

    assert response.status_code == 403


@pytest.mark.parametrize("role", ["owner", "boss"])
def test_change_role_answers_422_for_a_role_that_cannot_be_given(
    client: TestClient, redis_client: Redis, clock: MovableClock, role: str
) -> None:
    """
    GIVEN the owner of "Our Flat" added Maruf
    WHEN  they try to make Maruf "owner", or a role that doesn't exist
    THEN  it answers 422: only member and manager can be given
    """
    sign_up_owner(client, redis_client, clock)
    member_id = add_maruf(client)

    response = client.put(f"/api/v1/members/{member_id}/role", json={"role": role})

    assert response.status_code == 422


def test_deactivated_member_is_logged_out_at_once(
    client: TestClient, session: Session, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN Maruf is a member of "Our Flat", logged in on his own phone
    WHEN  the owner deactivates him from today
    THEN  Maruf's next request on that phone answers 401 (FR-80)
    """
    sign_up_owner(client, redis_client, clock)
    member_id = add_maruf(client)
    maruf = session.get_one(Membership, uuid.UUID(member_id))
    # Maruf's phone: its own client, with its own cookies.
    with TestClient(client.app, base_url="https://testserver") as marufs_phone:
        marufs_phone.cookies.set(
            SESSION_COOKIE,
            sessions.create_session(redis_client, maruf.person_id, clock()),
        )
        before = marufs_phone.get("/api/v1/me").json()["data"]
        assert before["membership"]["name"] == "Maruf", "the phone is Maruf's"

        client.post(
            f"/api/v1/members/{member_id}/deactivate", json={"on": "2026-11-21"}
        )

        assert marufs_phone.get("/api/v1/me").status_code == 401


def test_deactivate_answers_422_without_a_date(
    client: TestClient, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN the owner of "Our Flat" added Maruf
    WHEN  they deactivate Maruf without saying from when
    THEN  it answers 422
    """
    sign_up_owner(client, redis_client, clock)
    member_id = add_maruf(client)

    response = client.post(f"/api/v1/members/{member_id}/deactivate", json={})

    assert response.status_code == 422


def test_reactivate_answers_422_without_a_date(
    client: TestClient, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN the owner of "Our Flat" added Maruf and deactivated him
    WHEN  they reactivate Maruf without saying from when
    THEN  it answers 422
    """
    sign_up_owner(client, redis_client, clock)
    member_id = add_maruf(client)
    client.post(f"/api/v1/members/{member_id}/deactivate", json={"on": "2026-11-21"})

    response = client.post(f"/api/v1/members/{member_id}/reactivate", json={})

    assert response.status_code == 422


def test_members_list_includes_deactivated_members_with_their_status(
    client: TestClient, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN the owner of "Our Flat" added Maruf and deactivated him
    WHEN  they ask for the members list
    THEN  Maruf is in it, as inactive, for the Past tab
    """
    sign_up_owner(client, redis_client, clock)
    member_id = add_maruf(client)
    client.post(f"/api/v1/members/{member_id}/deactivate", json={"on": "2026-11-21"})

    response = client.get("/api/v1/members")

    statuses = {m["name"]: m["status"] for m in response.json()["data"]}
    assert statuses == {"Maruf": "inactive", "Rabbi Hasan": "active"}


@pytest.mark.parametrize(
    ("method", "action", "body"),
    [
        pytest.param("PUT", "role", {"role": "manager"}, id="role"),
        pytest.param("POST", "deactivate", {"on": "2026-11-21"}, id="deactivate"),
        pytest.param("POST", "reactivate", {"on": "2026-12-01"}, id="reactivate"),
    ],
)
def test_status_and_role_changes_answer_404_for_another_homes_member(
    client: TestClient,
    session: Session,
    redis_client: Redis,
    clock: MovableClock,
    method: str,
    action: str,
    body: dict[str, Any],
) -> None:
    """
    GIVEN the owner of "Our Flat" is logged in, and Karim is in "Old Fort"
    WHEN  they change Karim's role, deactivate him or reactivate him
    THEN  each answers 404, and Karim stays as he was
    """
    sign_up_owner(client, redis_client, clock)
    karim = member_of_old_fort(session)

    response = client.request(method, f"/api/v1/members/{karim.id}/{action}", json=body)

    assert response.status_code == 404
    assert "Karim" not in response.text
    session.refresh(karim)
    assert (karim.role, karim.status) == ("member", "active")


def rabbi_joins_old_fort(session: Session) -> uuid.UUID:
    """Make Rabbi (01712 345678) an active member of "Old Fort"; its id."""
    person = session.exec(select(Person).where(Person.phone == PHONE_E164)).one()
    old_fort = homes_service.create_home(
        session, name="Old Fort", area="Dhanmondi", first_month=date(2026, 1, 1)
    )
    session.add(Membership(home_id=old_fort.id, person_id=person.id, name="Rabbi"))
    session.flush()
    return old_fort.id


def test_person_in_two_homes_chooses_one_after_log_in(
    client: TestClient,
    session: Session,
    redis_client: Redis,
    notifier: FakeNotifier,
    clock: MovableClock,
) -> None:
    """
    GIVEN Rabbi owns "Our Flat" and is a member of "Old Fort"
    WHEN  he logs in, and then opens Old Fort by naming it
    THEN  log-in lists both homes without choosing one, a request naming no
          home is refused with "choose_home", and naming Old Fort opens it
          as a member
    """
    sign_up_owner(client, redis_client, clock)
    old_fort_id = rabbi_joins_old_fort(session)
    client.post("/api/v1/auth/log-out")
    clock.advance(timedelta(minutes=2))
    client.post("/api/v1/auth/codes", json={"contact": PHONE})

    logged_in = client.post(
        "/api/v1/auth/log-in",
        json={"contact": PHONE, "code": notifier.last_code_to(PHONE_E164)},
    ).json()["data"]
    unnamed = client.get("/api/v1/me")
    named = client.get("/api/v1/me", headers={"X-Colivo-Home": str(old_fort_id)})

    assert logged_in["me"] is None
    assert [home["name"] for home in logged_in["homes"]] == ["Old Fort", "Our Flat"]
    assert unnamed.status_code == 409
    assert unnamed.json()["data"] == {"reason": "choose_home"}
    me = named.json()["data"]
    assert (me["home"]["name"], me["membership"]["role"]) == ("Old Fort", "member")


def test_my_homes_lists_active_homes_without_a_header(
    client: TestClient, session: Session, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN Rabbi owns "Our Flat", is a member of "Old Fort", and was a member
          of "Green House" (deactivated)
    WHEN  he asks for his homes, naming none
    THEN  it lists Old Fort and Our Flat with his role, and not Green House
    """
    sign_up_owner(client, redis_client, clock)
    rabbi_joins_old_fort(session)
    person = session.exec(select(Person).where(Person.phone == PHONE_E164)).one()
    green_house = homes_service.create_home(
        session, name="Green House", area=None, first_month=date(2026, 1, 1)
    )
    session.add(
        Membership(
            home_id=green_house.id,
            person_id=person.id,
            name="Rabbi",
            status=MembershipStatus.INACTIVE,
        )
    )
    session.flush()

    response = client.get("/api/v1/me/homes")

    assert response.status_code == 200
    homes = [(home["name"], home["role"]) for home in response.json()["data"]]
    assert homes == [("Old Fort", "member"), ("Our Flat", "owner")]


def test_me_shows_the_chosen_homes_first_log_in_check(
    client: TestClient, session: Session, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN Rabbi owns "Our Flat" (details checked at sign-up) and was just
          added to "Old Fort" (not checked yet)
    WHEN  he asks who he is, naming Old Fort, then Our Flat
    THEN  Old Fort's answer shows its check still to do; Our Flat's is done
    """
    sign_up_owner(client, redis_client, clock)
    our_flat_id = owner_home_id(client)
    old_fort_id = rabbi_joins_old_fort(session)

    in_old_fort = client.get("/api/v1/me", headers={HOME_HEADER: str(old_fort_id)})
    in_our_flat = client.get("/api/v1/me", headers={HOME_HEADER: str(our_flat_id)})

    old_fort, our_flat = in_old_fort.json()["data"], in_our_flat.json()["data"]
    assert (old_fort["home"]["name"], old_fort["membership"]["details_checked"]) == (
        "Old Fort",
        False,
    )
    assert (our_flat["home"]["name"], our_flat["membership"]["details_checked"]) == (
        "Our Flat",
        True,
    )


def test_me_lists_the_persons_homes_for_the_switcher(
    client: TestClient, session: Session, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN Rabbi owns "Our Flat" and is a member of "Old Fort"
    WHEN  he asks who he is in Our Flat
    THEN  the answer lists both his homes, for switching
    """
    sign_up_owner(client, redis_client, clock)
    our_flat_id = owner_home_id(client)
    rabbi_joins_old_fort(session)

    response = client.get("/api/v1/me", headers={HOME_HEADER: str(our_flat_id)})

    homes = [home["name"] for home in response.json()["data"]["homes"]]
    assert homes == ["Old Fort", "Our Flat"]


def test_adding_a_member_without_naming_a_home_changes_nothing(
    client: TestClient, session: Session, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN Rabbi owns "Our Flat" and is a member of "Old Fort"
    WHEN  he adds Maruf without naming a home
    THEN  it is refused with 409 "choose_home", and Maruf is in no home
    """
    sign_up_owner(client, redis_client, clock)
    rabbi_joins_old_fort(session)

    response = client.post("/api/v1/members", json=maruf_body())

    assert response.status_code == 409
    assert response.json()["data"] == {"reason": "choose_home"}
    assert members_named(session, "Maruf") == 0


def test_log_out_works_without_choosing_a_home(
    client: TestClient, session: Session, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN Rabbi owns "Our Flat" and is a member of "Old Fort"
    WHEN  he logs out without naming a home
    THEN  he is logged out: the next request needs a log-in
    """
    sign_up_owner(client, redis_client, clock)
    rabbi_joins_old_fort(session)

    response = client.post("/api/v1/auth/log-out")

    assert response.status_code == 200
    assert client.get("/api/v1/me/homes").status_code == 401


def test_not_in_home_answer_is_the_same_for_any_home(
    client: TestClient, session: Session, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN Rabbi owns "Our Flat", and Karim's "Old Fort" exists
    WHEN  Rabbi names Old Fort, and then a home id that doesn't exist
    THEN  both answers are the same 403, and neither names Old Fort
    """
    sign_up_owner(client, redis_client, clock)
    old_fort_id = member_of_old_fort(session).home_id

    other = client.get("/api/v1/me", headers={HOME_HEADER: str(old_fort_id)})
    unknown = client.get("/api/v1/me", headers={HOME_HEADER: str(uuid.uuid7())})

    assert (other.status_code, unknown.status_code) == (403, 403)
    assert other.json() == unknown.json()
    assert "Old Fort" not in other.text


def test_my_homes_answers_401_with_no_active_home(
    client: TestClient, session: Session, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN Hijam is logged in, and his only home deactivates him
    WHEN  his open page asks for his homes
    THEN  it answers 401: he is logged out at once
    """
    sign_up_owner(client, redis_client, clock)
    log_in_as_new(client, session, redis_client, clock, role=Role.MEMBER)
    hijam = session.exec(select(Membership).where(Membership.name == "Hijam")).one()
    hijam.status = MembershipStatus.INACTIVE
    session.flush()

    response = client.get("/api/v1/me/homes")

    assert response.status_code == 401


def test_role_follows_the_chosen_home(
    client: TestClient, session: Session, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN Rabbi owns "Our Flat" and is a plain member of "Old Fort"
    WHEN  he asks for the members list in each home
    THEN  Our Flat answers it; Old Fort refuses with 403 for his role there
    """
    sign_up_owner(client, redis_client, clock)
    our_flat_id = owner_home_id(client)
    old_fort_id = rabbi_joins_old_fort(session)

    in_our_flat = client.get("/api/v1/members", headers={HOME_HEADER: str(our_flat_id)})
    in_old_fort = client.get("/api/v1/members", headers={HOME_HEADER: str(old_fort_id)})

    assert in_our_flat.status_code == 200
    assert in_old_fort.status_code == 403
    assert in_old_fort.json().get("data") is None


def test_home_header_that_is_not_an_id_answers_422(
    client: TestClient, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN Rabbi owns "Our Flat"
    WHEN  a request names the home "our-flat", which isn't a home id
    THEN  it answers 422, saying which header is wrong
    """
    sign_up_owner(client, redis_client, clock)

    response = client.get("/api/v1/me", headers={HOME_HEADER: "our-flat"})

    assert response.status_code == 422
    assert "x-colivo-home" in response.json()["errors"][0].lower()


MARUF_EMAIL = "maruf@example.com"


def log_in_with(
    client: TestClient, notifier: FakeNotifier, contact: str, to: str
) -> dict[str, Any]:
    """Log out, then log in with ``contact`` and the code sent to ``to``."""
    client.post("/api/v1/auth/log-out")
    client.post("/api/v1/auth/codes", json={"contact": contact})
    return client.post(
        "/api/v1/auth/log-in",
        json={"contact": contact, "code": notifier.last_code_to(to)},
    ).json()


def test_owner_adds_an_email_to_a_member_with_a_code(
    client: TestClient, redis_client: Redis, notifier: FakeNotifier, clock: MovableClock
) -> None:
    """
    GIVEN Rabbi Hasan owns "Our Flat" and added Maruf by phone
    WHEN  he asks for a code to Maruf's email and saves it with that code
    THEN  Maruf has both, and logs in with the email and with the phone
    """
    sign_up_owner(client, redis_client, clock)
    member_id = add_maruf(client)

    sent = client.post(
        f"/api/v1/members/{member_id}/contact/code", json={"contact": MARUF_EMAIL}
    )
    saved = client.put(
        f"/api/v1/members/{member_id}/contact",
        json={"contact": MARUF_EMAIL, "code": notifier.last_code_to(MARUF_EMAIL)},
    )
    # The change code to the email used this minute's send (FR-94).
    clock.advance(timedelta(minutes=1))
    by_email = log_in_with(client, notifier, MARUF_EMAIL, MARUF_EMAIL)
    by_phone = log_in_with(client, notifier, MARUF_PHONE, MARUF_E164)

    assert sent.status_code == 200
    assert saved.status_code == 200
    assert (saved.json()["data"]["phone"], saved.json()["data"]["email"]) == (
        MARUF_E164,
        MARUF_EMAIL,
    )
    assert by_email["data"]["me"]["membership"]["name"] == "Maruf"
    assert by_phone["data"]["me"]["membership"]["name"] == "Maruf"


def test_member_contact_code_goes_to_the_new_contact(
    client: TestClient, redis_client: Redis, notifier: FakeNotifier, clock: MovableClock
) -> None:
    """
    GIVEN the owner of "Our Flat" added Maruf by phone
    WHEN  POST /api/v1/members/{id}/contact/code is sent for maruf@example.com
    THEN  it answers 200, and the code goes to the email, not to Maruf's phone
    """
    sign_up_owner(client, redis_client, clock)
    member_id = add_maruf(client)
    notifier.sent.clear()

    response = client.post(
        f"/api/v1/members/{member_id}/contact/code", json={"contact": MARUF_EMAIL}
    )

    assert response.status_code == 200
    assert response.json()["data"]["channel"] == "email"
    assert [message.to for message in notifier.sent] == [MARUF_EMAIL]


def give_maruf_an_email(
    client: TestClient, notifier: FakeNotifier, member_id: str
) -> None:
    """The logged-in owner adds maruf@example.com to Maruf, with its code."""
    client.post(
        f"/api/v1/members/{member_id}/contact/code", json={"contact": MARUF_EMAIL}
    )
    client.put(
        f"/api/v1/members/{member_id}/contact",
        json={"contact": MARUF_EMAIL, "code": notifier.last_code_to(MARUF_EMAIL)},
    )


def test_removing_a_members_email_answers_200_with_the_member(
    client: TestClient, redis_client: Redis, notifier: FakeNotifier, clock: MovableClock
) -> None:
    """
    GIVEN Maruf logs in with a phone and an email
    WHEN  DELETE /api/v1/members/{id}/contact/email is sent
    THEN  it answers 200 with Maruf, who has only his phone now
    """
    sign_up_owner(client, redis_client, clock)
    member_id = add_maruf(client)
    give_maruf_an_email(client, notifier, member_id)

    response = client.delete(f"/api/v1/members/{member_id}/contact/email")

    assert response.status_code == 200
    member = response.json()["data"]
    assert (member["phone"], member["email"]) == (MARUF_E164, None)


def test_removing_an_unknown_kind_of_contact_answers_422(
    client: TestClient, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN the owner of "Our Flat" added Maruf
    WHEN  DELETE /api/v1/members/{id}/contact/fax is sent
    THEN  it answers 422
    """
    sign_up_owner(client, redis_client, clock)
    member_id = add_maruf(client)

    response = client.delete(f"/api/v1/members/{member_id}/contact/fax")

    assert response.status_code == 422


def test_saving_a_contact_with_a_wrong_code_answers_400_and_changes_nothing(
    client: TestClient, redis_client: Redis, notifier: FakeNotifier, clock: MovableClock
) -> None:
    """
    GIVEN a code was sent to maruf@example.com for Maruf
    WHEN  PUT /api/v1/members/{id}/contact is sent with another code
    THEN  it answers 400 "wrong" with 4 tries left, and Maruf has no email
    """
    sign_up_owner(client, redis_client, clock)
    member_id = add_maruf(client)
    client.post(
        f"/api/v1/members/{member_id}/contact/code", json={"contact": MARUF_EMAIL}
    )
    wrong = "000000" if notifier.last_code_to(MARUF_EMAIL) != "000000" else "111111"

    response = client.put(
        f"/api/v1/members/{member_id}/contact",
        json={"contact": MARUF_EMAIL, "code": wrong},
    )

    assert response.status_code == 400
    assert response.json()["data"] == {"reason": "wrong", "tries_left": 4}
    listed = client.get("/api/v1/members").json()["data"]
    assert [each["email"] for each in listed if each["id"] == member_id] == [None]


def test_saving_someone_elses_phone_answers_409_and_changes_nothing(
    client: TestClient, redis_client: Redis, notifier: FakeNotifier, clock: MovableClock
) -> None:
    """
    GIVEN Rabbi Hasan logs in with 01712 345678 and added Maruf
    WHEN  he saves 01712 345678 for Maruf with the right code
    THEN  it answers 409, and Maruf keeps his own phone
    """
    sign_up_owner(client, redis_client, clock)
    member_id = add_maruf(client)
    # Rabbi's sign-up code used this minute's send to his phone (FR-94).
    clock.advance(timedelta(minutes=1))
    client.post(f"/api/v1/members/{member_id}/contact/code", json={"contact": PHONE})

    response = client.put(
        f"/api/v1/members/{member_id}/contact",
        json={"contact": PHONE, "code": notifier.last_code_to(PHONE_E164)},
    )

    assert response.status_code == 409
    assert (
        response.json()["message"] == "Someone else logs in with that phone or email."
    )
    listed = client.get("/api/v1/members").json()["data"]
    assert [each["phone"] for each in listed if each["id"] == member_id] == [MARUF_E164]


def test_contact_code_answers_the_same_for_someone_elses_phone(
    client: TestClient, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN Rabbi Hasan logs in with 01712 345678 and added Maruf
    WHEN  codes are asked for Maruf to 01712 345678 (taken) and 01912 345678 (free)
    THEN  both answer 200 with the same body
    """
    sign_up_owner(client, redis_client, clock)
    member_id = add_maruf(client)
    clock.advance(timedelta(minutes=1))
    url = f"/api/v1/members/{member_id}/contact/code"

    taken = client.post(url, json={"contact": PHONE})
    free = client.post(url, json={"contact": "01912 345678"})

    assert (taken.status_code, free.status_code) == (200, 200)
    assert taken.json() == free.json()


def maruf_joins_old_fort(
    session: Session, status: MembershipStatus = MembershipStatus.ACTIVE
) -> None:
    """Make Maruf (01812 345678) a member of another home, "Old Fort"."""
    person = session.exec(select(Person).where(Person.phone == MARUF_E164)).one()
    old_fort = homes_service.create_home(
        session, name="Old Fort", area="Dhanmondi", first_month=date(2026, 1, 1)
    )
    session.add(
        Membership(
            home_id=old_fort.id, person_id=person.id, name="Maruf", status=status
        )
    )
    session.flush()


# The three ways the owner or a manager changes a member's log-in: method,
# path after /members/{id}, and body.
CONTACT_CALLS = [
    pytest.param("POST", "contact/code", {"contact": MARUF_EMAIL}, id="code"),
    pytest.param(
        "PUT", "contact", {"contact": MARUF_EMAIL, "code": "123456"}, id="save"
    ),
    pytest.param("DELETE", "contact/phone", None, id="remove"),
]


@pytest.mark.parametrize(("method", "path", "body"), CONTACT_CALLS)
def test_a_member_in_another_home_is_refused_403(
    client: TestClient,
    session: Session,
    redis_client: Redis,
    notifier: FakeNotifier,
    clock: MovableClock,
    method: str,
    path: str,
    body: dict[str, Any] | None,
) -> None:
    """
    GIVEN Maruf, a member of "Our Flat", is also active in "Old Fort"
    WHEN  the owner of Our Flat asks for a code, saves or removes his log-in
    THEN  it answers 403 "Only they can change …", and nothing is sent
    """
    sign_up_owner(client, redis_client, clock)
    member_id = add_maruf(client)
    maruf_joins_old_fort(session)
    notifier.sent.clear()

    response = client.request(method, f"/api/v1/members/{member_id}/{path}", json=body)

    assert response.status_code == 403
    assert response.json()["message"] == (
        "Only they can change their log-in, from My profile."
    )
    assert notifier.sent == []


def test_members_list_says_whose_log_in_can_be_changed(
    client: TestClient, session: Session, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN Maruf is also in "Old Fort", and Sumi is only in "Our Flat"
    WHEN  the owner of Our Flat reads the members list
    THEN  Maruf's log-in can't be changed and Sumi's can, and nothing in the
          list is about Old Fort
    """
    sign_up_owner(client, redis_client, clock)
    add_maruf(client)
    client.post("/api/v1/members", json=maruf_body(name="Sumi", contact="01912 345678"))
    maruf_joins_old_fort(session)

    listed = client.get("/api/v1/members").json()["data"]

    editable = {each["name"]: each["contact_editable"] for each in listed}
    assert (editable["Maruf"], editable["Sumi"]) == (False, True)
    assert set(listed[0]) == {
        "id",
        "name",
        "phone",
        "email",
        "role",
        "status",
        "joined_on",
        "contact_editable",
    }
