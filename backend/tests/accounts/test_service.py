from datetime import date

import pytest
from redis import Redis
from sqlmodel import Session, select

from app.core.notifier import Channel
from app.modules.accounts import codes, service
from app.modules.accounts.contact import Contact
from app.modules.accounts.models import MembershipPeriod, MembershipStatus, Role
from app.modules.accounts.schemas import SignUpIn
from app.modules.homes.models import Home
from tests.conftest import MovableClock

PHONE_E164 = "+8801712345678"


def sign_up_data(contact: Contact, code: str, **changes: object) -> SignUpIn:
    """The sign-up form for "Our Flat", with any field changed."""
    fields: dict[str, object] = {
        "contact": contact,
        "code": code,
        "name": "Rabbi Hasan",
        "home_name": "Our Flat",
        "area": "Mirpur",
        "first_month": date(2026, 11, 1),
        "lives_here": True,
    }
    return SignUpIn.model_validate(fields | changes)


def test_sign_up_creates_the_home_and_its_owner(
    session: Session, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN a valid code for 01712 345678
    WHEN  Rabbi Hasan signs up, creating "Our Flat" in Mirpur from November 2026
    THEN  the home exists with those details, and Rabbi Hasan is its active owner
    """
    contact = Contact(channel=Channel.SMS, value=PHONE_E164)
    code = codes.issue_code(redis_client, contact, clock())

    membership = service.sign_up(
        session, redis_client, sign_up_data(contact, code), clock()
    )

    home = session.get(Home, membership.home_id)
    assert home is not None
    assert (home.name, home.area, home.first_month) == (
        "Our Flat",
        "Mirpur",
        date(2026, 11, 1),
    )
    assert (membership.name, membership.role, membership.status) == (
        "Rabbi Hasan",
        Role.OWNER,
        MembershipStatus.ACTIVE,
    )


@pytest.mark.parametrize(
    ("lives_here", "stays"),
    [
        pytest.param(True, [(date(2026, 11, 1), None)], id="lives here"),
        pytest.param(False, [], id="runs the home only"),
    ],
)
def test_owner_stay_follows_i_live_here_too(
    session: Session,
    redis_client: Redis,
    clock: MovableClock,
    lives_here: bool,
    stays: list[tuple[date, date | None]],
) -> None:
    """
    GIVEN a sign-up for "Our Flat" from November 2026
    WHEN  "I live here too" is ticked, or not
    THEN  ticked, the owner has one open stay from 1 November (they pay);
          not ticked, they have none (never charged)
    """
    contact = Contact(channel=Channel.SMS, value=PHONE_E164)
    code = codes.issue_code(redis_client, contact, clock())

    membership = service.sign_up(
        session,
        redis_client,
        sign_up_data(contact, code, lives_here=lives_here),
        clock(),
    )

    periods = session.exec(
        select(MembershipPeriod).where(MembershipPeriod.membership_id == membership.id)
    ).all()
    assert [(period.starts_on, period.ends_on) for period in periods] == stays
