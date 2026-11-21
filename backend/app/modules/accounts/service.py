import uuid
from datetime import date, datetime

from redis import Redis
from sqlmodel import Session, func, select
from starlette.exceptions import HTTPException

from app.core.notifier import Channel, Notifier
from app.modules.accounts import codes, sessions
from app.modules.accounts.constants import CODE_LIFETIME, CODE_RESEND_AFTER
from app.modules.accounts.contact import Contact
from app.modules.accounts.models import (
    Membership,
    MembershipPeriod,
    MembershipStatus,
    Person,
    Role,
)
from app.modules.accounts.schemas import (
    CodeSentOut,
    LogInIn,
    MeHomeOut,
    MemberIn,
    MemberOut,
    MeMembershipOut,
    MeOut,
    MePersonOut,
    SignUpIn,
)
from app.modules.homes import service as homes_service
from app.modules.homes.constants import DEFAULT_TIME_ZONE
from app.modules.homes.models import Home

NOT_ADDED = (
    "Not added yet. Ask your home's owner or manager to add you, or create a new home."
)


def find_person(session: Session, contact: Contact) -> Person | None:
    """Return the person who logs in with ``contact``, if anyone does.

    Args:
        session: The database session.
        contact: A phone or email.

    Returns:
        The person, or None.
    """
    column = Person.email if contact.channel == Channel.EMAIL else Person.phone
    return session.exec(select(Person).where(column == contact.value)).first()


def new_person(contact: Contact) -> Person:
    """A person who logs in with ``contact``: their phone or their email.

    Args:
        contact: A phone or email.

    Returns:
        The new person, not yet added to the session.
    """
    if contact.channel == Channel.EMAIL:
        return Person(email=contact.value)
    return Person(phone=contact.value)


def active_membership(session: Session, person: Person) -> Membership | None:
    """Return the person's active membership; there is at most one (FR-85).

    Args:
        session: The database session.
        person: The person.

    Returns:
        The membership, or None when they are active nowhere.
    """
    return session.exec(
        select(Membership).where(
            Membership.person_id == person.id,
            Membership.status == MembershipStatus.ACTIVE,
        )
    ).first()


def sign_up(
    session: Session, redis_client: Redis, data: SignUpIn, now: datetime
) -> Membership:
    """Create a home and make the person signing up its owner (FR-83).

    The person, the home, the owner's membership and, when they live there,
    their stay from the first month are saved in one transaction.

    Args:
        session: The database session.
        redis_client: Where one-time codes are kept.
        data: The sign-up form, with the code sent to its contact.
        now: The current time.

    Returns:
        The owner's new membership.

    Raises:
        HTTPException: 400 for a first month that isn't this month or next;
            409 when the person is already active in a home (FR-85).
    """
    # The first month says nothing about who someone is, so it is checked
    # before the code (a wrong month doesn't use the code up). "Already in a
    # home" is told only to someone with the right code.
    homes_service.check_first_month(data.first_month, now, DEFAULT_TIME_ZONE)
    codes.use_code(redis_client, data.contact, data.code, now)
    person = find_person(session, data.contact) or new_person(data.contact)
    if active_membership(session, person) is not None:
        raise HTTPException(409, "You're already in a home. Log in instead.")
    home = homes_service.create_home(
        session, name=data.home_name, area=data.area, first_month=data.first_month
    )
    # No ORM relationships, so the session doesn't order inserts by foreign
    # key: flush the parents first.
    session.add(person)
    session.flush()
    membership = Membership(
        home_id=home.id, person_id=person.id, name=data.name, role=Role.OWNER
    )
    session.add(membership)
    if data.lives_here:
        # "I live here too": the owner pays from the first month; otherwise
        # they run the home without a stay and are never charged.
        session.flush()
        session.add(
            MembershipPeriod(
                home_id=home.id,
                membership_id=membership.id,
                starts_on=data.first_month,
            )
        )
    session.commit()
    session.refresh(membership)
    return membership


def get_me(session: Session, membership: Membership) -> MeOut:
    """Describe who is logged in through ``membership``, and their home.

    Args:
        session: The database session.
        membership: The logged-in membership.

    Returns:
        The person, the membership and the home.
    """
    person = session.get_one(Person, membership.person_id)
    home = session.get_one(Home, membership.home_id)
    return MeOut(
        person=MePersonOut.model_validate(person, from_attributes=True),
        membership=MeMembershipOut.model_validate(membership, from_attributes=True),
        home=MeHomeOut.model_validate(home, from_attributes=True),
    )


def request_code(
    redis_client: Redis, notifier: Notifier, contact: Contact, now: datetime
) -> CodeSentOut:
    """Send a one-time code to ``contact`` by SMS or email (FR-94).

    The answer is the same whether or not anyone uses ``contact``, so nobody
    can find out who has an account.

    Args:
        redis_client: Where codes are kept.
        notifier: Sends the SMS or email.
        contact: The phone or email to send it to.
        now: The current time.

    Returns:
        How it was sent, how long it works and when a new one can be sent.
    """
    code = codes.issue_code(redis_client, contact, now)
    minutes = int(CODE_LIFETIME.total_seconds() // 60)
    notifier.send(
        contact.channel,
        contact.value,
        f"Your Colivo code is {code}. It works for {minutes} minutes.",
    )
    return CodeSentOut(
        channel=contact.channel,
        expires_in_seconds=int(CODE_LIFETIME.total_seconds()),
        resend_in_seconds=int(CODE_RESEND_AFTER.total_seconds()),
    )


def log_out(redis_client: Redis, token: str) -> None:
    """End the session behind ``token``.

    Args:
        redis_client: Where sessions are kept.
        token: The session cookie's token.
    """
    sessions.end_session(redis_client, token)


def log_in(
    session: Session, redis_client: Redis, data: LogInIn, now: datetime
) -> Membership:
    """Log in with a one-time code (FR-84): into the person's one active home.

    Args:
        session: The database session.
        redis_client: Where one-time codes are kept.
        data: The phone or email, and the code sent to it.
        now: The current time.

    Returns:
        The person's active membership.

    Raises:
        HTTPException: 404 "Not added yet" when the person is active in no
            home: never added, or deactivated (FR-87).
    """
    codes.use_code(redis_client, data.contact, data.code, now)
    person = find_person(session, data.contact)
    membership = person and active_membership(session, person)
    if not membership:
        # Only after the right code, so nobody learns who has an account.
        raise HTTPException(404, NOT_ADDED)
    return membership


def add_member(
    session: Session,
    notifier: Notifier,
    adder: Membership,
    data: MemberIn,
    now: datetime,
) -> Membership:
    """Add a member to the adder's home, and tell them so (FR-79).

    The notice goes out only after the member is saved, so nobody is told
    they were added when they weren't.

    Args:
        session: The database session.
        notifier: Sends the SMS or email.
        adder: The owner or manager adding them.
        data: The new member's name, phone or email, join date and role.
        now: The current time.

    Returns:
        The new membership.
    """
    person = find_person(session, data.contact) or new_person(data.contact)
    session.add(person)
    session.flush()
    member = Membership(
        home_id=adder.home_id,
        person_id=person.id,
        name=data.name,
        role=data.role,
        created_by=adder.id,
    )
    session.add(member)
    session.flush()
    session.add(
        MembershipPeriod(
            home_id=adder.home_id, membership_id=member.id, starts_on=data.joined_on
        )
    )
    session.commit()
    session.refresh(member)
    home = session.get_one(Home, adder.home_id)
    notifier.send(
        data.contact.channel,
        data.contact.value,
        f"{adder.name} added you to {home.name} on Colivo. "
        "Log in with this phone or email and a one-time code.",
    )
    return member


def joined_on(session: Session, membership: Membership) -> date | None:
    """The member's join date: the start of their first stay; None for none.

    Args:
        session: The database session.
        membership: The member.

    Returns:
        The date, or None for an owner who doesn't live in the home.
    """
    return session.exec(
        select(func.min(MembershipPeriod.starts_on)).where(
            MembershipPeriod.membership_id == membership.id
        )
    ).one()


def member_out(session: Session, membership: Membership) -> MemberOut:
    """Describe a member for the members list.

    Args:
        session: The database session.
        membership: The member.

    Returns:
        Their name, phone or email, role, status and join date.
    """
    person = session.get_one(Person, membership.person_id)
    return MemberOut(
        id=membership.id,
        name=membership.name,
        phone=person.phone,
        email=person.email,
        role=membership.role,
        status=membership.status,
        joined_on=joined_on(session, membership),
    )


def list_members(session: Session, home_id: uuid.UUID) -> list[MemberOut]:
    """Everyone in a home, A to Z, for the owner and managers.

    Args:
        session: The database session.
        home_id: The home.

    Returns:
        The members, active and deactivated.
    """
    members = session.exec(
        select(Membership)
        .where(Membership.home_id == home_id)
        .order_by(func.lower(Membership.name))
    ).all()
    return [member_out(session, member) for member in members]
