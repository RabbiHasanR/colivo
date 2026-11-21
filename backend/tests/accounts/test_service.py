from contextlib import AbstractContextManager, nullcontext
from datetime import UTC, date, datetime

import pytest
from redis import Redis
from sqlmodel import Session, func, select
from starlette.exceptions import HTTPException

from app.core.notifier import Channel
from app.modules.accounts import codes, service
from app.modules.accounts.contact import Contact, parse_contact
from app.modules.accounts.models import (
    Membership,
    MembershipPeriod,
    MembershipStatus,
    Person,
    Role,
)
from app.modules.accounts.schemas import SignUpIn
from app.modules.homes import service as homes_service
from app.modules.homes.models import Home
from tests.conftest import FakeNotifier, MovableClock

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


@pytest.mark.parametrize(
    ("first_month", "outcome"),
    [
        pytest.param(date(2026, 12, 1), nullcontext(), id="this month"),
        pytest.param(date(2027, 1, 1), nullcontext(), id="next month"),
        pytest.param(date(2026, 11, 1), pytest.raises(HTTPException), id="last month"),
        pytest.param(date(2027, 2, 1), pytest.raises(HTTPException), id="in 2 months"),
        pytest.param(
            date(2026, 12, 15), pytest.raises(HTTPException), id="not the 1st"
        ),
    ],
)
def test_first_month_must_be_this_month_or_next(
    session: Session,
    redis_client: Redis,
    clock: MovableClock,
    first_month: date,
    outcome: AbstractContextManager[object],
) -> None:
    """
    GIVEN it is 30 Nov 2026, 19:00 UTC: already 1 December in Dhaka
    WHEN  someone signs up with a first month
    THEN  December and January are accepted; November, February and a
          mid-month date are refused with 400
    """
    clock.now = datetime(2026, 11, 30, 19, 0, tzinfo=UTC)
    contact = Contact(channel=Channel.SMS, value=PHONE_E164)
    code = codes.issue_code(redis_client, contact, clock())
    data = sign_up_data(contact, code, first_month=first_month)

    with outcome as error:
        service.sign_up(session, redis_client, data, clock())

    if isinstance(error, pytest.ExceptionInfo):
        assert error.value.status_code == 400


def sign_up_with_new_code(
    session: Session, redis_client: Redis, clock: MovableClock, **changes: object
) -> Membership:
    """Sign 01712 345678 up, with a fresh code and any form field changed."""
    contact = Contact(channel=Channel.SMS, value=PHONE_E164)
    code = codes.issue_code(redis_client, contact, clock())
    data = sign_up_data(contact, code, **changes)
    return service.sign_up(session, redis_client, data, clock())


def test_sign_up_refused_when_already_active_in_a_home(
    session: Session, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN 01712 345678 is the active owner of "Our Flat"
    WHEN  they sign up again to create "Second Home"
    THEN  it is refused with 409 ("log in instead"), and no second home exists
    """
    sign_up_with_new_code(session, redis_client, clock)

    with pytest.raises(HTTPException) as error:
        sign_up_with_new_code(session, redis_client, clock, home_name="Second Home")

    assert error.value.status_code == 409
    assert session.exec(select(func.count()).select_from(Home)).one() == 1


def test_person_no_longer_active_anywhere_can_sign_up(
    session: Session, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN 01712 345678 was a member of "Old Flat" and is now inactive there
    WHEN  they sign up to create "Our Flat"
    THEN  they own Our Flat, under the same person (one log-in)
    """
    person = Person(phone=PHONE_E164)
    old_flat = homes_service.create_home(
        session, name="Old Flat", area=None, first_month=date(2026, 1, 1)
    )
    session.add(person)
    session.flush()
    session.add(
        Membership(
            home_id=old_flat.id,
            person_id=person.id,
            name="Rabbi Hasan",
            status=MembershipStatus.INACTIVE,
        )
    )
    session.flush()

    membership = sign_up_with_new_code(session, redis_client, clock)

    assert membership.person_id == person.id


@pytest.mark.parametrize(
    "contact",
    [
        pytest.param(Contact(channel=Channel.SMS, value=PHONE_E164), id="phone"),
        pytest.param(
            Contact(channel=Channel.EMAIL, value="rabbi@example.com"), id="email"
        ),
    ],
)
def test_code_goes_by_sms_to_a_phone_and_by_email_to_an_email(
    redis_client: Redis, notifier: FakeNotifier, clock: MovableClock, contact: Contact
) -> None:
    """
    GIVEN a phone or an email
    WHEN  a code is asked for
    THEN  one message with a six-digit code goes to it: by SMS to the phone,
          by email to the email address
    """
    service.request_code(redis_client, notifier, contact, clock())

    [message] = notifier.sent
    assert (message.channel, message.to) == (contact.channel, contact.value)
    assert len(notifier.last_code_to(contact.value)) == 6


def test_email_in_any_letter_case_is_the_same_person(
    session: Session, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN Rabbi@Example.com signed up and owns "Our Flat"
    WHEN  rabbi@example.COM signs up for another home
    THEN  it is the same person, kept as rabbi@example.com, so it is refused
          with 409
    """
    first = Contact.model_validate(parse_contact("Rabbi@Example.com"))
    code = codes.issue_code(redis_client, first, clock())
    owner = service.sign_up(session, redis_client, sign_up_data(first, code), clock())
    again = Contact.model_validate(parse_contact("rabbi@example.COM"))
    code = codes.issue_code(redis_client, again, clock())

    with pytest.raises(HTTPException) as error:
        service.sign_up(
            session, redis_client, sign_up_data(again, code, home_name="Two"), clock()
        )

    assert error.value.status_code == 409
    person = session.get_one(Person, owner.person_id)
    assert (person.email, person.phone) == ("rabbi@example.com", None)
