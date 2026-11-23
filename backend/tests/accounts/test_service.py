import uuid
from contextlib import AbstractContextManager, nullcontext
from datetime import UTC, date, datetime, timedelta

import pytest
from redis import Redis
from sqlmodel import Session, col, func, select
from starlette.exceptions import HTTPException

from app.core.exceptions import AppError
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
from app.modules.accounts.schemas import (
    ContactChangeIn,
    ContactKind,
    DeactivateIn,
    HomeRefusalOut,
    HomeRefusalReason,
    LogInIn,
    MemberIn,
    MemberUpdateIn,
    MeUpdateIn,
    ReactivateIn,
    RoleIn,
    SignUpIn,
)
from app.modules.history.models import ChangeLog
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


def test_person_active_in_another_home_can_sign_up(
    session: Session, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN 01712 345678 is the active owner of "Our Flat"
    WHEN  they sign up again to create "Second Home"
    THEN  they own both homes as one person, and Our Flat is unchanged
    """
    first = sign_up_with_new_code(session, redis_client, clock)
    # A new code waits a minute after the last one (B11).
    clock.advance(timedelta(minutes=2))

    second = sign_up_with_new_code(
        session, redis_client, clock, home_name="Second Home"
    )

    assert second.person_id == first.person_id
    assert second.home_id != first.home_id
    session.refresh(first)
    assert (first.role, first.status) == (Role.OWNER, MembershipStatus.ACTIVE)


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
    THEN  that home's owner is the same person, kept as rabbi@example.com
    """
    first = Contact.model_validate(parse_contact("Rabbi@Example.com"))
    code = codes.issue_code(redis_client, first, clock())
    owner = service.sign_up(session, redis_client, sign_up_data(first, code), clock())
    # A new code waits a minute after the last one (B11).
    clock.advance(timedelta(minutes=2))
    again = Contact.model_validate(parse_contact("rabbi@example.COM"))
    code = codes.issue_code(redis_client, again, clock())

    second = service.sign_up(
        session, redis_client, sign_up_data(again, code, home_name="Two"), clock()
    )

    assert second.person_id == owner.person_id
    person = session.get_one(Person, owner.person_id)
    assert (person.email, person.phone) == ("rabbi@example.com", None)


def test_sign_up_refused_with_a_wrong_code(
    session: Session, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN a code was sent to 01712 345678
    WHEN  they sign up typing a different code
    THEN  it is refused with 400, and no home is created
    """
    contact = Contact(channel=Channel.SMS, value=PHONE_E164)
    code = codes.issue_code(redis_client, contact, clock())
    wrong = f"{(int(code) + 1) % 1_000_000:06d}"

    with pytest.raises(HTTPException) as error:
        service.sign_up(session, redis_client, sign_up_data(contact, wrong), clock())

    assert error.value.status_code == 400
    assert session.exec(select(func.count()).select_from(Home)).one() == 0


def test_log_in_with_one_home_returns_it(
    session: Session, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN 01712 345678 owns "Our Flat" and no other home
    WHEN  they log in with a new code
    THEN  the answer is their owner membership of Our Flat, the one home
    """
    owner = sign_up_with_new_code(session, redis_client, clock)
    clock.advance(timedelta(minutes=2))
    contact = Contact(channel=Channel.SMS, value=PHONE_E164)
    code = codes.issue_code(redis_client, contact, clock())

    person, answer = service.log_in(
        session, redis_client, LogInIn(contact=contact, code=code), clock()
    )

    assert person.id == owner.person_id
    assert answer.me is not None and answer.me.membership.id == owner.id
    assert [home.name for home in answer.homes] == ["Our Flat"]


def test_log_in_with_several_homes_lists_them_without_me(
    session: Session, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN 01712 345678 owns "Our Flat" (Mirpur) and is a member of "Old Fort"
    WHEN  they log in with a new code
    THEN  the answer lists both homes by name, with area and role, and
          chooses none
    """
    owner = sign_up_with_new_code(session, redis_client, clock)
    old_fort = homes_service.create_home(
        session, name="Old Fort", area=None, first_month=date(2026, 1, 1)
    )
    session.add(Membership(home_id=old_fort.id, person_id=owner.person_id, name="R"))
    session.flush()
    clock.advance(timedelta(minutes=2))
    contact = Contact(channel=Channel.SMS, value=PHONE_E164)
    code = codes.issue_code(redis_client, contact, clock())

    _, answer = service.log_in(
        session, redis_client, LogInIn(contact=contact, code=code), clock()
    )

    homes = [(home.name, home.area, home.role) for home in answer.homes]
    assert homes == [
        ("Old Fort", None, Role.MEMBER),
        ("Our Flat", "Mirpur", Role.OWNER),
    ]
    assert answer.me is None


def add_inactive_member(session: Session, phone: str) -> None:
    """Make ``phone`` a deactivated member of "Old Flat"."""
    person = Person(phone=phone)
    old_flat = homes_service.create_home(
        session, name="Old Flat", area=None, first_month=date(2026, 1, 1)
    )
    session.add(person)
    session.flush()
    session.add(
        Membership(
            home_id=old_flat.id,
            person_id=person.id,
            name="Maruf",
            status=MembershipStatus.INACTIVE,
        )
    )
    session.flush()


@pytest.mark.parametrize(
    "deactivated", [False, True], ids=["never added", "deactivated"]
)
def test_log_in_with_no_active_membership_is_not_added_yet(
    session: Session, redis_client: Redis, clock: MovableClock, deactivated: bool
) -> None:
    """
    GIVEN 01812 345678 was never added to a home, or was deactivated
    WHEN  they log in with the right code
    THEN  it answers 404 "Not added yet"
    """
    phone = "+8801812345678"
    if deactivated:
        add_inactive_member(session, phone)
    contact = Contact(channel=Channel.SMS, value=phone)
    code = codes.issue_code(redis_client, contact, clock())

    with pytest.raises(HTTPException) as error:
        service.log_in(
            session, redis_client, LogInIn(contact=contact, code=code), clock()
        )

    assert error.value.status_code == 404


MARUF_E164 = "+8801812345678"


def maruf(**changes: object) -> MemberIn:
    """Adding Maruf (01812 345678) as a member from 21 Nov 2026, with changes."""
    fields: dict[str, object] = {
        "name": "Maruf",
        "contact": Contact(channel=Channel.SMS, value=MARUF_E164),
        "joined_on": date(2026, 11, 21),
        "role": "member",
    }
    return MemberIn.model_validate(fields | changes)


def test_owner_adds_a_member_who_gets_a_notice(
    session: Session, redis_client: Redis, notifier: FakeNotifier, clock: MovableClock
) -> None:
    """
    GIVEN Rabbi Hasan owns "Our Flat"
    WHEN  he adds Maruf, joining on 21 Nov 2026
    THEN  Maruf is an active member of Our Flat added by Rabbi Hasan, staying
          from 21 Nov, and gets one SMS saying so
    """
    owner = sign_up_with_new_code(session, redis_client, clock)

    member = service.add_member(session, notifier, owner, maruf(), clock())

    assert (
        member.home_id,
        member.name,
        member.role,
        member.status,
        member.created_by,
    ) == (owner.home_id, "Maruf", Role.MEMBER, MembershipStatus.ACTIVE, owner.id)
    stays = session.exec(
        select(MembershipPeriod).where(MembershipPeriod.membership_id == member.id)
    ).all()
    assert [(stay.starts_on, stay.ends_on) for stay in stays] == [
        (date(2026, 11, 21), None)
    ]
    [notice] = notifier.sent
    assert (notice.channel, notice.to) == (Channel.SMS, MARUF_E164)
    assert "Rabbi Hasan added you to Our Flat" in notice.text


def add_maruf_to(session: Session, home_name: str, status: MembershipStatus) -> Person:
    """Make Maruf (01812 345678) a member of a new home called ``home_name``."""
    person = Person(phone=MARUF_E164)
    home = homes_service.create_home(
        session, name=home_name, area=None, first_month=date(2026, 1, 1)
    )
    session.add(person)
    session.flush()
    session.add(
        Membership(home_id=home.id, person_id=person.id, name="Maruf", status=status)
    )
    session.flush()
    return person


def maruf_memberships(session: Session, person: Person) -> int:
    """How many memberships Maruf has, in any home."""
    return session.exec(
        select(func.count())
        .select_from(Membership)
        .where(Membership.person_id == person.id)
    ).one()


def test_member_active_in_another_home_is_added(
    session: Session, redis_client: Redis, notifier: FakeNotifier, clock: MovableClock
) -> None:
    """
    GIVEN Maruf is an active member of "Old Flat"
    WHEN  the owner of "Our Flat" adds him
    THEN  he is active in both homes, and is told he was added to Our Flat
    """
    owner = sign_up_with_new_code(session, redis_client, clock)
    person = add_maruf_to(session, "Old Flat", MembershipStatus.ACTIVE)

    service.add_member(session, notifier, owner, maruf(), clock())

    statuses = session.exec(
        select(Membership.status).where(Membership.person_id == person.id)
    ).all()
    assert statuses == [MembershipStatus.ACTIVE, MembershipStatus.ACTIVE]
    assert any(m.to == MARUF_E164 and "Our Flat" in m.text for m in notifier.sent), (
        "Maruf was told he was added to Our Flat"
    )


def add_past_member(
    session: Session, home_id: uuid.UUID, name: str = "Maruf"
) -> Person:
    """Make Maruf (01812 345678) a deactivated member of ``home_id``."""
    person = Person(phone=MARUF_E164)
    session.add(person)
    session.flush()
    session.add(
        Membership(
            home_id=home_id,
            person_id=person.id,
            name=name,
            status=MembershipStatus.INACTIVE,
        )
    )
    session.flush()
    return person


def test_deactivated_member_of_this_home_is_not_added_again(
    session: Session, redis_client: Redis, notifier: FakeNotifier, clock: MovableClock
) -> None:
    """
    GIVEN Maruf was a member of "Our Flat" and was deactivated
    WHEN  the owner adds him again
    THEN  it is refused with 409, saying to reactivate him instead
    """
    owner = sign_up_with_new_code(session, redis_client, clock)
    person = add_past_member(session, owner.home_id)

    with pytest.raises(HTTPException) as error:
        service.add_member(session, notifier, owner, maruf(), clock())

    assert error.value.status_code == 409
    assert "Reactivate" in str(error.value.detail)
    assert maruf_memberships(session, person) == 1


def test_active_member_of_this_home_cannot_be_added_again(
    session: Session, redis_client: Redis, notifier: FakeNotifier, clock: MovableClock
) -> None:
    """
    GIVEN Maruf is an active member of "Our Flat"
    WHEN  the owner adds his phone again, under another name
    THEN  it is refused with 409 "Already a member of this home.", with no
          second membership and no notice
    """
    owner = sign_up_with_new_code(session, redis_client, clock)
    member = service.add_member(session, notifier, owner, maruf(), clock())
    notifier.sent.clear()

    with pytest.raises(HTTPException) as error:
        service.add_member(
            session, notifier, owner, maruf().model_copy(update={"name": "M"}), clock()
        )

    assert (error.value.status_code, error.value.detail) == (
        409,
        "Already a member of this home.",
    )
    person = session.get_one(Person, member.person_id)
    assert (maruf_memberships(session, person), notifier.sent) == (1, [])


OTHER_PHONE = "+8801912345678"


@pytest.mark.parametrize("name", ["Maruf", "maruf"])
def test_two_active_members_cannot_share_a_name(
    session: Session,
    redis_client: Redis,
    notifier: FakeNotifier,
    clock: MovableClock,
    name: str,
) -> None:
    """
    GIVEN Maruf is an active member of "Our Flat"
    WHEN  the owner adds someone else named "Maruf" or "maruf"
    THEN  it is refused with 409: names are unique among active members (FR-04)
    """
    owner = sign_up_with_new_code(session, redis_client, clock)
    service.add_member(session, notifier, owner, maruf(), clock())
    other = Contact(channel=Channel.SMS, value=OTHER_PHONE)

    with pytest.raises(HTTPException) as error:
        service.add_member(
            session, notifier, owner, maruf(name=name, contact=other), clock()
        )

    assert error.value.status_code == 409


def test_a_deactivated_members_name_can_be_used_again(
    session: Session, redis_client: Redis, notifier: FakeNotifier, clock: MovableClock
) -> None:
    """
    GIVEN an earlier Maruf left "Our Flat" and was deactivated
    WHEN  the owner adds a new person also named Maruf
    THEN  the new Maruf is added: only active members' names must differ
    """
    owner = sign_up_with_new_code(session, redis_client, clock)
    add_past_member(session, owner.home_id)
    newcomer = Contact(channel=Channel.SMS, value=OTHER_PHONE)

    member = service.add_member(
        session, notifier, owner, maruf(contact=newcomer), clock()
    )

    assert member.name == "Maruf"


def stays_of(session: Session, member: Membership) -> list[tuple[date, date | None]]:
    """A member's stays, as (starts_on, ends_on), earliest first."""
    stays = session.exec(
        select(MembershipPeriod)
        .where(MembershipPeriod.membership_id == member.id)
        .order_by(col(MembershipPeriod.starts_on))
    ).all()
    return [(stay.starts_on, stay.ends_on) for stay in stays]


def test_owner_changes_a_members_name_and_join_date(
    session: Session, redis_client: Redis, notifier: FakeNotifier, clock: MovableClock
) -> None:
    """
    GIVEN Maruf joined "Our Flat" on 21 Nov 2026
    WHEN  the owner renames him "Maruf Hossain" and moves his join date to 1 Nov
    THEN  his name is "Maruf Hossain" and his first stay starts on 1 Nov
    """
    owner = sign_up_with_new_code(session, redis_client, clock)
    member = service.add_member(session, notifier, owner, maruf(), clock())

    changed = service.update_member(
        session,
        owner,
        member.id,
        MemberUpdateIn(name="Maruf Hossain", joined_on=date(2026, 11, 1)),
        clock(),
    )

    assert changed.name == "Maruf Hossain"
    assert stays_of(session, changed) == [(date(2026, 11, 1), None)]


def test_join_date_cannot_be_after_the_end_of_the_first_stay(
    session: Session, redis_client: Redis, notifier: FakeNotifier, clock: MovableClock
) -> None:
    """
    GIVEN Maruf's first stay in "Our Flat" ran from 21 to 25 Nov 2026, and the
          owner doesn't live there (no stay)
    WHEN  Maruf's join date is moved to 28 Nov, or the owner is given one
    THEN  both are refused with 400
    """
    owner = sign_up_with_new_code(session, redis_client, clock, lives_here=False)
    member = service.add_member(session, notifier, owner, maruf(), clock())
    stay = service.first_stay(session, member)
    assert stay is not None
    stay.ends_on = date(2026, 11, 25)
    session.flush()
    late = MemberUpdateIn(joined_on=date(2026, 11, 28))

    for target in (member, owner):
        with pytest.raises(HTTPException) as error:
            service.update_member(session, owner, target.id, late, clock())
        assert error.value.status_code == 400, target.name


def test_new_name_cannot_be_one_already_taken(
    session: Session, redis_client: Redis, notifier: FakeNotifier, clock: MovableClock
) -> None:
    """
    GIVEN Rabbi Hasan owns "Our Flat", and Maruf is a member
    WHEN  Maruf is renamed "rabbi hasan"
    THEN  it is refused with 409: an active member already has that name
    """
    owner = sign_up_with_new_code(session, redis_client, clock)
    member = service.add_member(session, notifier, owner, maruf(), clock())

    with pytest.raises(HTTPException) as error:
        service.update_member(
            session, owner, member.id, MemberUpdateIn(name="rabbi hasan"), clock()
        )

    assert error.value.status_code == 409


def test_me_says_who_added_the_member_and_whether_they_checked(
    session: Session, redis_client: Redis, notifier: FakeNotifier, clock: MovableClock
) -> None:
    """
    GIVEN Rabbi Hasan signed up "Our Flat" and added Maruf, joining 21 Nov 2026
    WHEN  each of them asks who is logged in
    THEN  Maruf was added by Rabbi Hasan and hasn't checked his details yet;
          Rabbi Hasan, who signed up himself, has
    """
    owner = sign_up_with_new_code(session, redis_client, clock)
    member = service.add_member(session, notifier, owner, maruf(), clock())

    for_member = service.get_me(session, member).membership
    for_owner = service.get_me(session, owner).membership

    assert (
        for_member.joined_on,
        for_member.added_by_name,
        for_member.details_checked,
    ) == (date(2026, 11, 21), "Rabbi Hasan", False)
    assert (for_owner.added_by_name, for_owner.details_checked) == (None, True)


def test_member_fixes_their_name_and_checks_their_details(
    session: Session, redis_client: Redis, notifier: FakeNotifier, clock: MovableClock
) -> None:
    """
    GIVEN Maruf was added to "Our Flat" and hasn't checked his details yet
    WHEN  at his first log-in he fixes his name to "Maruf Hossain"
    THEN  his name is fixed, and his details are checked as of now
    """
    owner = sign_up_with_new_code(session, redis_client, clock)
    member = service.add_member(session, notifier, owner, maruf(), clock())

    changed = service.update_me(
        session, member, MeUpdateIn(name="Maruf Hossain"), clock()
    )

    assert (changed.name, changed.details_checked_at) == ("Maruf Hossain", clock())


def history_of(session: Session, member: Membership) -> list[ChangeLog]:
    """The change log rows about a member, oldest first."""
    return list(
        session.exec(
            select(ChangeLog)
            .where(ChangeLog.entity_id == member.id)
            .order_by(col(ChangeLog.created_at), col(ChangeLog.id))
        ).all()
    )


@pytest.mark.parametrize("change", ["added", "changed by the owner", "own name fixed"])
def test_adding_and_changing_members_is_recorded(
    session: Session,
    redis_client: Redis,
    notifier: FakeNotifier,
    clock: MovableClock,
    change: str,
) -> None:
    """
    GIVEN the owner of "Our Flat" added Maruf, joining 21 Nov 2026
    WHEN  nothing else happens; or the owner renames him and moves his join
          date; or Maruf fixes his own name
    THEN  the history keeps each change: who made it, how, and the old and
          new values
    """
    owner = sign_up_with_new_code(session, redis_client, clock)
    member = service.add_member(session, notifier, owner, maruf(), clock())
    if change == "changed by the owner":
        service.update_member(
            session,
            owner,
            member.id,
            MemberUpdateIn(name="Maruf Hossain", joined_on=date(2026, 11, 1)),
            clock(),
        )
    if change == "own name fixed":
        service.update_me(session, member, MeUpdateIn(name="Maruf H."), clock())

    rows = [
        (row.entity, row.action, row.changed_by, row.old_values, row.new_values)
        for row in history_of(session, member)
    ]

    added = (
        "membership",
        "create",
        owner.id,
        None,
        {"name": "Maruf", "role": "member", "joined_on": "2026-11-21"},
    )
    expected = {
        "added": [added],
        "changed by the owner": [
            added,
            (
                "membership",
                "update",
                owner.id,
                {"name": "Maruf", "joined_on": "2026-11-21"},
                {"name": "Maruf Hossain", "joined_on": "2026-11-01"},
            ),
        ],
        "own name fixed": [
            added,
            (
                "membership",
                "update",
                member.id,
                {"name": "Maruf"},
                {"name": "Maruf H."},
            ),
        ],
    }
    assert rows == expected[change]


@pytest.mark.parametrize(
    ("before", "after"),
    [
        pytest.param(Role.MEMBER, Role.MANAGER, id="make manager"),
        pytest.param(Role.MANAGER, Role.MEMBER, id="remove manager"),
    ],
)
def test_owner_makes_a_member_a_manager_and_back(
    session: Session,
    redis_client: Redis,
    notifier: FakeNotifier,
    clock: MovableClock,
    before: Role,
    after: Role,
) -> None:
    """
    GIVEN Maruf is a member (or a manager) of "Our Flat"
    WHEN  the owner makes him a manager (or a member again)
    THEN  his role changes, and the history keeps who changed it, old and new
    """
    owner = sign_up_with_new_code(session, redis_client, clock)
    member = service.add_member(session, notifier, owner, maruf(role=before), clock())

    changed = service.change_role(
        session, owner, member.id, RoleIn.model_validate({"role": after}), clock()
    )

    assert changed.role == after
    last = history_of(session, member)[-1]
    assert (last.action, last.changed_by, last.old_values, last.new_values) == (
        "update",
        owner.id,
        {"role": before.value},
        {"role": after.value},
    )


def test_owners_own_role_cannot_change(
    session: Session, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN Rabbi Hasan owns "Our Flat"
    WHEN  his own role is set to member
    THEN  it is refused with 400: a home always has its owner (FR-63)
    """
    owner = sign_up_with_new_code(session, redis_client, clock)

    with pytest.raises(HTTPException) as error:
        service.change_role(session, owner, owner.id, RoleIn(role=Role.MEMBER), clock())

    assert error.value.status_code == 400


def test_deactivating_closes_the_stay_on_the_chosen_date(
    session: Session, redis_client: Redis, notifier: FakeNotifier, clock: MovableClock
) -> None:
    """
    GIVEN Maruf has lived in "Our Flat" since 1 Nov 2026 (today is 21 Nov)
    WHEN  the owner deactivates him from 20 Nov
    THEN  he is inactive, his stay ends on 20 Nov, and the history keeps it
    """
    owner = sign_up_with_new_code(session, redis_client, clock)
    member = service.add_member(
        session, notifier, owner, maruf(joined_on=date(2026, 11, 1)), clock()
    )

    gone = service.deactivate(
        session, owner, member.id, DeactivateIn(on=date(2026, 11, 20)), clock()
    )

    assert gone.status == MembershipStatus.INACTIVE
    assert stays_of(session, gone) == [(date(2026, 11, 1), date(2026, 11, 20))]
    last = history_of(session, gone)[-1]
    assert (last.action, last.changed_by, last.old_values, last.new_values) == (
        "update",
        owner.id,
        {"status": "active"},
        {"status": "inactive", "on": "2026-11-20"},
    )


@pytest.mark.parametrize(
    "on",
    [
        pytest.param(date(2026, 11, 22), id="tomorrow"),
        pytest.param(date(2026, 10, 31), id="before he joined"),
    ],
)
def test_deactivation_date_must_be_today_or_earlier_and_in_the_stay(
    session: Session,
    redis_client: Redis,
    notifier: FakeNotifier,
    clock: MovableClock,
    on: date,
) -> None:
    """
    GIVEN Maruf has lived in "Our Flat" since 1 Nov 2026, and today is 21 Nov
    WHEN  the owner deactivates him from tomorrow, or from 31 Oct
    THEN  it is refused with 400
    """
    owner = sign_up_with_new_code(session, redis_client, clock)
    member = service.add_member(
        session, notifier, owner, maruf(joined_on=date(2026, 11, 1)), clock()
    )

    with pytest.raises(HTTPException) as error:
        service.deactivate(session, owner, member.id, DeactivateIn(on=on), clock())

    assert error.value.status_code == 400


def test_inactive_member_cannot_be_deactivated_again(
    session: Session, redis_client: Redis, notifier: FakeNotifier, clock: MovableClock
) -> None:
    """
    GIVEN Maruf was deactivated from today
    WHEN  the owner deactivates him again
    THEN  it is refused with 409
    """
    owner = sign_up_with_new_code(session, redis_client, clock)
    member = service.add_member(session, notifier, owner, maruf(), clock())
    today = DeactivateIn(on=date(2026, 11, 21))
    service.deactivate(session, owner, member.id, today, clock())

    with pytest.raises(HTTPException) as error:
        service.deactivate(session, owner, member.id, today, clock())

    assert error.value.status_code == 409


TODAY = date(2026, 11, 21)


def test_owner_cannot_be_deactivated(
    session: Session, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN Rabbi Hasan owns "Our Flat" and lives there
    WHEN  he is deactivated
    THEN  it is refused with 400: the owner always stays (FR-63)
    """
    owner = sign_up_with_new_code(session, redis_client, clock)

    with pytest.raises(HTTPException) as error:
        service.deactivate(session, owner, owner.id, DeactivateIn(on=TODAY), clock())

    assert error.value.status_code == 400


def test_manager_cannot_deactivate_another_manager(
    session: Session, redis_client: Redis, notifier: FakeNotifier, clock: MovableClock
) -> None:
    """
    GIVEN "Our Flat" has two managers, Hijam and Maruf
    WHEN  Hijam deactivates Maruf
    THEN  it is refused with 403: removing a manager is the owner's call
    """
    owner = sign_up_with_new_code(session, redis_client, clock)
    hijam = service.add_member(
        session,
        notifier,
        owner,
        maruf(
            name="Hijam",
            contact=Contact(channel=Channel.SMS, value=OTHER_PHONE),
            role="manager",
        ),
        clock(),
    )
    manager = service.add_member(
        session, notifier, owner, maruf(role="manager"), clock()
    )

    with pytest.raises(HTTPException) as error:
        service.deactivate(session, hijam, manager.id, DeactivateIn(on=TODAY), clock())

    assert error.value.status_code == 403


def maruf_who_left(
    session: Session, notifier: FakeNotifier, owner: Membership, clock: MovableClock
) -> Membership:
    """Maruf, who lived in "Our Flat" from 1 to 20 Nov 2026 and was deactivated."""
    member = service.add_member(
        session, notifier, owner, maruf(joined_on=date(2026, 11, 1)), clock()
    )
    return service.deactivate(
        session, owner, member.id, DeactivateIn(on=date(2026, 11, 20)), clock()
    )


def test_reactivating_opens_a_new_stay_from_the_chosen_date(
    session: Session, redis_client: Redis, notifier: FakeNotifier, clock: MovableClock
) -> None:
    """
    GIVEN Maruf lived in "Our Flat" from 1 to 20 Nov 2026 and was deactivated
    WHEN  the owner reactivates him, charges starting again on 1 Dec
    THEN  he is active, his old stay is kept, a new one starts on 1 Dec, and
          the history keeps it
    """
    owner = sign_up_with_new_code(session, redis_client, clock)
    member = maruf_who_left(session, notifier, owner, clock)

    back = service.reactivate(
        session, owner, member.id, ReactivateIn(on=date(2026, 12, 1)), clock()
    )

    assert back.status == MembershipStatus.ACTIVE
    assert stays_of(session, back) == [
        (date(2026, 11, 1), date(2026, 11, 20)),
        (date(2026, 12, 1), None),
    ]
    last = history_of(session, back)[-1]
    assert (last.action, last.old_values, last.new_values) == (
        "update",
        {"status": "inactive"},
        {"status": "active", "on": "2026-12-01"},
    )


def test_reactivation_date_must_be_after_the_deactivation(
    session: Session, redis_client: Redis, notifier: FakeNotifier, clock: MovableClock
) -> None:
    """
    GIVEN Maruf's stay in "Our Flat" ended on 20 Nov 2026
    WHEN  he is reactivated from 20 Nov, the same day
    THEN  it is refused with 400: charges start again after he left
    """
    owner = sign_up_with_new_code(session, redis_client, clock)
    member = maruf_who_left(session, notifier, owner, clock)

    with pytest.raises(HTTPException) as error:
        service.reactivate(
            session, owner, member.id, ReactivateIn(on=date(2026, 11, 20)), clock()
        )

    assert error.value.status_code == 400


def test_active_member_cannot_be_reactivated(
    session: Session, redis_client: Redis, notifier: FakeNotifier, clock: MovableClock
) -> None:
    """
    GIVEN Maruf is an active member of "Our Flat"
    WHEN  he is reactivated from 1 Dec 2026
    THEN  it is refused with 409
    """
    owner = sign_up_with_new_code(session, redis_client, clock)
    member = service.add_member(session, notifier, owner, maruf(), clock())

    with pytest.raises(HTTPException) as error:
        service.reactivate(
            session, owner, member.id, ReactivateIn(on=date(2026, 12, 1)), clock()
        )

    assert error.value.status_code == 409


def test_member_who_joined_another_home_can_be_reactivated(
    session: Session, redis_client: Redis, notifier: FakeNotifier, clock: MovableClock
) -> None:
    """
    GIVEN Maruf left "Our Flat" and is now an active member of "Old Fort"
    WHEN  Our Flat's owner reactivates him
    THEN  he is active in both homes
    """
    owner = sign_up_with_new_code(session, redis_client, clock)
    member = maruf_who_left(session, notifier, owner, clock)
    old_fort = homes_service.create_home(
        session, name="Old Fort", area=None, first_month=date(2026, 11, 1)
    )
    in_old_fort = Membership(
        home_id=old_fort.id, person_id=member.person_id, name="Maruf"
    )
    session.add(in_old_fort)
    session.flush()

    service.reactivate(
        session, owner, member.id, ReactivateIn(on=date(2026, 12, 1)), clock()
    )

    session.refresh(in_old_fort)
    statuses = (member.status, in_old_fort.status)
    assert statuses == (MembershipStatus.ACTIVE, MembershipStatus.ACTIVE)


def test_reactivating_into_a_taken_name_is_refused(
    session: Session, redis_client: Redis, notifier: FakeNotifier, clock: MovableClock
) -> None:
    """
    GIVEN Maruf left "Our Flat", and since then another Maruf joined
    WHEN  the first Maruf is reactivated
    THEN  it is refused with 409: an active member already has the name
    """
    owner = sign_up_with_new_code(session, redis_client, clock)
    member = maruf_who_left(session, notifier, owner, clock)
    newcomer = Contact(channel=Channel.SMS, value=OTHER_PHONE)
    service.add_member(session, notifier, owner, maruf(contact=newcomer), clock())

    with pytest.raises(HTTPException) as error:
        service.reactivate(
            session, owner, member.id, ReactivateIn(on=date(2026, 12, 1)), clock()
        )

    assert error.value.status_code == 409


def hijam_the_manager(
    session: Session, notifier: FakeNotifier, owner: Membership, clock: MovableClock
) -> Membership:
    """Hijam, a manager of "Our Flat"."""
    return service.add_member(
        session,
        notifier,
        owner,
        maruf(
            name="Hijam",
            contact=Contact(channel=Channel.SMS, value=OTHER_PHONE),
            role="manager",
        ),
        clock(),
    )


def test_manager_cannot_reactivate_a_manager(
    session: Session, redis_client: Redis, notifier: FakeNotifier, clock: MovableClock
) -> None:
    """
    GIVEN the owner deactivated Maruf, a manager of "Our Flat"
    WHEN  Hijam, another manager, reactivates him
    THEN  it is refused with 403, and Maruf stays deactivated: bringing a
          manager back is the owner's call
    """
    owner = sign_up_with_new_code(session, redis_client, clock)
    hijam = hijam_the_manager(session, notifier, owner, clock)
    manager = service.add_member(
        session,
        notifier,
        owner,
        maruf(role="manager", joined_on=date(2026, 11, 1)),
        clock(),
    )
    service.deactivate(
        session, owner, manager.id, DeactivateIn(on=date(2026, 11, 20)), clock()
    )

    with pytest.raises(HTTPException) as error:
        service.reactivate(
            session, hijam, manager.id, ReactivateIn(on=date(2026, 12, 1)), clock()
        )

    assert error.value.status_code == 403
    session.refresh(manager)
    assert manager.status == MembershipStatus.INACTIVE


def test_manager_cannot_change_the_owners_details(
    session: Session, redis_client: Redis, notifier: FakeNotifier, clock: MovableClock
) -> None:
    """
    GIVEN Rabbi Hasan owns "Our Flat", living there since 1 Nov 2026, and
          Hijam is a manager
    WHEN  Hijam renames the owner and moves his join date
    THEN  it is refused with 403, and the owner's details stay as they were
    """
    owner = sign_up_with_new_code(session, redis_client, clock)
    hijam = hijam_the_manager(session, notifier, owner, clock)

    with pytest.raises(HTTPException) as error:
        service.update_member(
            session,
            hijam,
            owner.id,
            MemberUpdateIn(name="Somebody Else", joined_on=date(2026, 11, 15)),
            clock(),
        )

    assert error.value.status_code == 403
    session.refresh(owner)
    assert owner.name == "Rabbi Hasan"
    assert stays_of(session, owner) == [(date(2026, 11, 1), None)]


@pytest.mark.parametrize(
    "change",
    [
        pytest.param(MemberUpdateIn(name="Maruf Hossain"), id="rename"),
        pytest.param(DeactivateIn(on=date(2026, 11, 21)), id="deactivate"),
    ],
)
def test_changing_a_person_in_one_home_leaves_the_other_home_unchanged(
    session: Session,
    redis_client: Redis,
    notifier: FakeNotifier,
    clock: MovableClock,
    change: MemberUpdateIn | DeactivateIn,
) -> None:
    """
    GIVEN Maruf is an active member of "Old Flat" with an open stay, and of
          "Our Flat"
    WHEN  Our Flat's owner renames or deactivates him
    THEN  his Old Flat membership keeps its name, its active status and its
          open stay
    """
    owner = sign_up_with_new_code(session, redis_client, clock)
    person = add_maruf_to(session, "Old Flat", MembershipStatus.ACTIVE)
    in_old_flat = session.exec(
        select(Membership).where(Membership.person_id == person.id)
    ).one()
    session.add(
        MembershipPeriod(
            home_id=in_old_flat.home_id,
            membership_id=in_old_flat.id,
            starts_on=date(2026, 1, 1),
        )
    )
    session.flush()
    member = service.add_member(session, notifier, owner, maruf(), clock())

    if isinstance(change, MemberUpdateIn):
        service.update_member(session, owner, member.id, change, clock())
    else:
        service.deactivate(session, owner, member.id, change, clock())

    session.refresh(in_old_flat)
    assert (in_old_flat.name, in_old_flat.status) == (
        "Maruf",
        MembershipStatus.ACTIVE,
    )
    open_stays = session.exec(
        select(MembershipPeriod).where(
            MembershipPeriod.membership_id == in_old_flat.id,
            col(MembershipPeriod.ends_on).is_(None),
        )
    ).all()
    assert len(open_stays) == 1


def rabbi_in_old_fort_too(session: Session, owner: Membership) -> Membership:
    """Make the owner of "Our Flat" an active member of "Old Fort" as well."""
    old_fort = homes_service.create_home(
        session, name="Old Fort", area=None, first_month=date(2026, 1, 1)
    )
    member = Membership(home_id=old_fort.id, person_id=owner.person_id, name="R")
    session.add(member)
    session.flush()
    return member


def test_no_home_named_with_one_home_uses_it(
    session: Session, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN 01712 345678 owns "Our Flat" and no other home
    WHEN  a request of theirs names no home
    THEN  it acts in Our Flat
    """
    owner = sign_up_with_new_code(session, redis_client, clock)
    person = session.get_one(Person, owner.person_id)

    assert service.membership_for(session, person, None).id == owner.id


def test_no_home_named_with_several_homes_is_refused(
    session: Session, redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN 01712 345678 owns "Our Flat" and is a member of "Old Fort"
    WHEN  a request of theirs names no home
    THEN  it is refused with 409 "Choose a home.", reason choose_home
    """
    owner = sign_up_with_new_code(session, redis_client, clock)
    rabbi_in_old_fort_too(session, owner)
    person = session.get_one(Person, owner.person_id)

    with pytest.raises(AppError) as error:
        service.membership_for(session, person, None)

    assert (error.value.status_code, error.value.detail) == (409, "Choose a home.")
    assert error.value.data == HomeRefusalOut(reason=HomeRefusalReason.CHOOSE_HOME)


@pytest.mark.parametrize(
    "which", ["inactive there", "another person's home", "no such home"]
)
def test_naming_a_home_the_person_is_not_active_in_is_refused(
    session: Session, redis_client: Redis, clock: MovableClock, which: str
) -> None:
    """
    GIVEN 01712 345678 owns "Our Flat"; they left "Old Fort"; "Green House"
          is someone else's
    WHEN  a request of theirs names Old Fort, Green House or an unknown id
    THEN  each is refused with the same 403, reason not_in_home
    """
    owner = sign_up_with_new_code(session, redis_client, clock)
    old_fort = rabbi_in_old_fort_too(session, owner)
    old_fort.status = MembershipStatus.INACTIVE
    green_house = homes_service.create_home(
        session, name="Green House", area=None, first_month=date(2026, 1, 1)
    )
    session.flush()
    home_id = {
        "inactive there": old_fort.home_id,
        "another person's home": green_house.id,
        "no such home": uuid.uuid7(),
    }[which]
    person = session.get_one(Person, owner.person_id)

    with pytest.raises(AppError) as error:
        service.membership_for(session, person, home_id)

    assert (error.value.status_code, error.value.detail) == (
        403,
        "You're no longer a member of this home.",
    )
    assert error.value.data == HomeRefusalOut(reason=HomeRefusalReason.NOT_IN_HOME)


# Phase 1c: changing the phone or email a member logs in with.

MARUF_EMAIL = "maruf@example.com"


def email(value: str = MARUF_EMAIL) -> Contact:
    """An email to log in with."""
    return Contact(channel=Channel.EMAIL, value=value)


def phone(value: str) -> Contact:
    """A phone (E.164) to log in with."""
    return Contact(channel=Channel.SMS, value=value)


def owner_and_maruf(
    session: Session, redis_client: Redis, notifier: FakeNotifier, clock: MovableClock
) -> tuple[Membership, Membership]:
    """Rabbi Hasan owns "Our Flat" and has added Maruf by phone; no messages yet."""
    owner = sign_up_with_new_code(session, redis_client, clock)
    member = service.add_member(session, notifier, owner, maruf(), clock())
    notifier.sent.clear()
    return owner, member


def change_with_code(
    session: Session,
    redis_client: Redis,
    notifier: FakeNotifier,
    clock: MovableClock,
    editor: Membership,
    member: Membership,
    contact: Contact,
) -> Membership:
    """``editor`` asks for a code to ``contact`` and saves it for ``member``."""
    service.request_member_contact_code(
        session, redis_client, notifier, editor, member.id, contact, clock()
    )
    data = ContactChangeIn(contact=contact, code=notifier.last_code_to(contact.value))
    return service.set_member_contact(
        session, redis_client, notifier, editor, member.id, data, clock()
    )


def person_of(session: Session, member: Membership) -> Person:
    """The person behind ``member``, read again from the database."""
    person = session.get_one(Person, member.person_id)
    session.refresh(person)
    return person


def test_adding_an_email_keeps_the_phone(
    session: Session, redis_client: Redis, notifier: FakeNotifier, clock: MovableClock
) -> None:
    """
    GIVEN Maruf logs in with 01812 345678
    WHEN  the owner adds maruf@example.com with the code sent to it
    THEN  Maruf has both the phone and the email
    """
    owner, member = owner_and_maruf(session, redis_client, notifier, clock)

    change_with_code(session, redis_client, notifier, clock, owner, member, email())

    person = person_of(session, member)
    assert (person.phone, person.email) == (MARUF_E164, MARUF_EMAIL)


def test_changing_the_phone_replaces_the_old_one(
    session: Session, redis_client: Redis, notifier: FakeNotifier, clock: MovableClock
) -> None:
    """
    GIVEN Maruf logs in with 01812 345678
    WHEN  the owner changes it to 01912 345678 with the code sent to it
    THEN  the old phone finds nobody, and the new one finds Maruf
    """
    owner, member = owner_and_maruf(session, redis_client, notifier, clock)

    change_with_code(
        session, redis_client, notifier, clock, owner, member, phone("+8801912345678")
    )

    assert service.find_person(session, phone(MARUF_E164)) is None
    found = service.find_person(session, phone("+8801912345678"))
    assert found is not None and found.id == member.person_id


def maruf_with_both(
    session: Session, redis_client: Redis, notifier: FakeNotifier, clock: MovableClock
) -> tuple[Membership, Membership]:
    """Maruf logs in with 01812 345678 and maruf@example.com; no messages yet."""
    owner, member = owner_and_maruf(session, redis_client, notifier, clock)
    change_with_code(session, redis_client, notifier, clock, owner, member, email())
    notifier.sent.clear()
    return owner, member


def test_removing_the_email_keeps_only_the_phone(
    session: Session, redis_client: Redis, notifier: FakeNotifier, clock: MovableClock
) -> None:
    """
    GIVEN Maruf logs in with a phone and an email
    WHEN  the owner removes the email
    THEN  Maruf has only the phone, and the email finds nobody
    """
    owner, member = maruf_with_both(session, redis_client, notifier, clock)

    service.remove_member_contact(
        session, redis_client, notifier, owner, member.id, ContactKind.EMAIL, clock()
    )

    person = person_of(session, member)
    assert (person.phone, person.email) == (MARUF_E164, None)
    assert service.find_person(session, email()) is None
