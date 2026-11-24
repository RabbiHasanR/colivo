import uuid

import pytest
from fastapi.testclient import TestClient
from redis import Redis
from sqlmodel import Session

from app.core.notifier import Channel
from app.modules.accounts import codes, sessions
from app.modules.accounts.constants import SESSION_COOKIE
from app.modules.accounts.contact import Contact
from app.modules.accounts.models import Membership, Person, Role
from tests.accounts.test_api import maruf_body, sign_up_owner
from tests.conftest import MovableClock


def test_setup_answers_403_for_a_member(
    client: TestClient, session: Session, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN "Our Flat", whose owner signed up, and Maruf, a member there
    WHEN  Maruf asks for the setup checklist
    THEN  it answers 403: the checklist is for the owner and managers
    """
    owner = Contact(channel=Channel.SMS, value="+8801712345678")
    signed_up = client.post(
        "/api/v1/auth/sign-up",
        json={
            "contact": owner.value,
            "code": codes.issue_code(redis_client, owner, clock()),
            "name": "Rabbi Hasan",
            "home_name": "Our Flat",
            "first_month": "2026-11-01",
            "lives_here": True,
        },
    )
    home_id = uuid.UUID(signed_up.json()["data"]["home"]["id"])
    maruf = Person(phone="+8801812345678")
    session.add(maruf)
    session.flush()
    session.add(
        Membership(home_id=home_id, person_id=maruf.id, name="Maruf", role=Role.MEMBER)
    )
    session.flush()
    token = sessions.create_session(redis_client, maruf.id, clock())
    client.cookies.clear()

    response = client.get(
        "/api/v1/home/setup", headers={"Cookie": f"{SESSION_COOKIE}={token}"}
    )

    assert response.status_code == 403


@pytest.mark.xfail(
    strict=True,
    reason="acceptance: the owner adds a room and puts members in it (B1, B6)",
)
def test_owner_adds_a_room_and_puts_a_member_in_it(
    client: TestClient, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN the owner of "Our Flat" is logged in
    WHEN  they add Room B (৳7,775, 2 beds) and add Maruf and Hijam to it
    THEN  Rooms lists Room B with both of them, each paying ৳3,887.50, and the
          members list shows them in Room B
    """
    sign_up_owner(client, redis_client, clock)

    added = client.post(
        "/api/v1/rooms", json={"name": "Room B", "rent": "7775.00", "beds": 2}
    )
    assert added.status_code == 201
    room_id = added.json()["data"]["id"]
    for body in (
        maruf_body(room_id=room_id),
        maruf_body(name="Hijam Shusil", contact="01911 223344", room_id=room_id),
    ):
        assert client.post("/api/v1/members", json=body).status_code == 201

    rooms = client.get("/api/v1/rooms").json()["data"]
    members = client.get("/api/v1/members").json()["data"]

    [room_b] = rooms["rooms"]
    assert (room_b["name"], room_b["rent"], room_b["beds"]) == ("Room B", "7775.00", 2)
    assert sorted(person["name"] for person in room_b["people"]) == [
        "Hijam Shusil",
        "Maruf",
    ]
    assert room_b["each_pays"] == "3887.50"
    assert (rooms["people"], rooms["rent_total"]) == (2, "7775.00")
    rooms_by_name = {
        member["name"]: member["room"] and member["room"]["name"] for member in members
    }
    assert rooms_by_name == {
        "Rabbi Hasan": None,
        "Maruf": "Room B",
        "Hijam Shusil": "Room B",
    }
