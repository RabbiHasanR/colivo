import uuid

from fastapi.testclient import TestClient
from redis import Redis
from sqlmodel import Session

from app.core.notifier import Channel
from app.modules.accounts import codes, sessions
from app.modules.accounts.constants import SESSION_COOKIE
from app.modules.accounts.contact import Contact
from app.modules.accounts.models import Membership, Person, Role
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
