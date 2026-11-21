import uuid
from datetime import date, datetime
from typing import Any

from redis import Redis
from sqlmodel import Session, col, func, select
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
    MemberUpdateIn,
    MeMembershipOut,
    MeOut,
    MePersonOut,
    MeUpdateIn,
    RoleIn,
    SignUpIn,
)
from app.modules.history import service as history
from app.modules.history.models import ChangeAction, ChangeEntity
from app.modules.homes import service as homes_service
from app.modules.homes.constants import DEFAULT_TIME_ZONE
from app.modules.homes.models import Home

ALREADY_IN_A_HOME = "This phone or email is already in a home."
PAST_MEMBER = "This person was a member of this home. Reactivate them instead."
NAME_TAKEN = "Someone in this home already has that name."
NO_STAY = "Only someone who lives in the home has a join date."
JOINED_AFTER_LEAVING = "The join date can't be after the end of their first stay."
MEMBER_NOT_FOUND = "Member not found."
OWNER_ROLE_FIXED = "The owner's role can't change."
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


def check_name_free(
    session: Session,
    home_id: uuid.UUID,
    name: str,
    except_id: uuid.UUID | None = None,
) -> None:
    """Refuse a name an active member of the home already has (FR-04).

    Letter case doesn't count: "Maruf" and "maruf" are the same name.

    Args:
        session: The database session.
        home_id: The home.
        name: The name wanted.
        except_id: A member whose own current name doesn't count (editing).

    Raises:
        HTTPException: 409 when the name is taken.
    """
    query = select(Membership.id).where(
        Membership.home_id == home_id,
        Membership.status == MembershipStatus.ACTIVE,
        func.lower(Membership.name) == name.lower(),
    )
    if except_id is not None:
        query = query.where(Membership.id != except_id)
    if session.exec(query).first():
        raise HTTPException(409, NAME_TAKEN)


def membership_in(
    session: Session, person: Person, home_id: uuid.UUID
) -> Membership | None:
    """The person's membership of one home, active or not (one per home).

    Args:
        session: The database session.
        person: The person.
        home_id: The home.

    Returns:
        The membership, or None if they were never in that home.
    """
    return session.exec(
        select(Membership).where(
            Membership.person_id == person.id, Membership.home_id == home_id
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
    # The owner signed up themselves: no first log-in check to show.
    membership = Membership(
        home_id=home.id,
        person_id=person.id,
        name=data.name,
        role=Role.OWNER,
        details_checked_at=now,
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
    adder = membership.created_by and session.get(Membership, membership.created_by)
    return MeOut(
        person=MePersonOut.model_validate(person, from_attributes=True),
        membership=MeMembershipOut(
            id=membership.id,
            name=membership.name,
            role=membership.role,
            status=membership.status,
            joined_on=joined_on(session, membership),
            added_by_name=adder.name if adder else None,
            details_checked=membership.details_checked_at is not None,
        ),
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

    Raises:
        HTTPException: 409 when the person is already active in a home, was
            a member of this one (they are reactivated instead), or an active
            member already has the name.
    """
    person = find_person(session, data.contact)
    if person and active_membership(session, person):
        # FR-85: one active home per person.
        raise HTTPException(409, ALREADY_IN_A_HOME)
    if person and membership_in(session, person, adder.home_id):
        raise HTTPException(409, PAST_MEMBER)
    check_name_free(session, adder.home_id, data.name)
    person = person or new_person(data.contact)
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
    record_member_change(
        session,
        member,
        changed_by=adder,
        action=ChangeAction.CREATE,
        new_values={
            "name": member.name,
            "role": member.role,
            "joined_on": data.joined_on.isoformat(),
        },
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


def update_member(
    session: Session,
    editor: Membership,
    member_id: uuid.UUID,
    data: MemberUpdateIn,
    now: datetime,
) -> Membership:
    """Change a member's name or join date (FR-86), for the owner or a manager.

    The join date is the start of the member's first stay, so that stay moves.

    Args:
        session: The database session.
        editor: The owner or manager making the change.
        member_id: The member to change.
        data: The new name or join date; what is left out stays.
        now: The current time.

    Returns:
        The changed membership.

    Raises:
        HTTPException: 404 for a member of another home; 400 for a join date
            they can't have; 409 for a name an active member already has.
    """
    member = get_member(session, editor.home_id, member_id)
    old_values: dict[str, Any] = {}
    new_values: dict[str, Any] = {}
    if data.name is not None and data.name != member.name:
        check_name_free(session, member.home_id, data.name, except_id=member.id)
        old_values["name"], new_values["name"] = member.name, data.name
        member.name = data.name
    if data.joined_on is not None:
        before = joined_on(session, member)
        move_join_date(session, member, data.joined_on)
        if before != data.joined_on:
            old_values["joined_on"] = before.isoformat() if before else None
            new_values["joined_on"] = data.joined_on.isoformat()
    if new_values:
        record_member_change(
            session,
            member,
            changed_by=editor,
            action=ChangeAction.UPDATE,
            old_values=old_values,
            new_values=new_values,
        )
    session.commit()
    session.refresh(member)
    return member


def get_member(
    session: Session, home_id: uuid.UUID, member_id: uuid.UUID
) -> Membership:
    """A member of ``home_id``; another home's members are never found.

    Args:
        session: The database session.
        home_id: The home the request is for.
        member_id: The member asked for.

    Returns:
        The membership.

    Raises:
        HTTPException: 404 for another home's member or an unknown id, so
            nobody learns another home's members exist (NFR-03).
    """
    member = session.get(Membership, member_id)
    if member is None or member.home_id != home_id:
        raise HTTPException(404, MEMBER_NOT_FOUND)
    return member


def first_stay(session: Session, member: Membership) -> MembershipPeriod | None:
    """The member's earliest stay, the one their join date belongs to.

    Args:
        session: The database session.
        member: The member.

    Returns:
        The stay, or None for an owner who doesn't live in the home.
    """
    return session.exec(
        select(MembershipPeriod)
        .where(MembershipPeriod.membership_id == member.id)
        .order_by(col(MembershipPeriod.starts_on))
    ).first()


def move_join_date(session: Session, member: Membership, joined_on: date) -> None:
    """Move the start of the member's first stay to ``joined_on``.

    Raises:
        HTTPException: 400 when they have no stay (an owner who doesn't live
            there), or the date is after the first stay ended.
    """
    stay = first_stay(session, member)
    if stay is None:
        raise HTTPException(400, NO_STAY)
    if stay.ends_on is not None and joined_on > stay.ends_on:
        raise HTTPException(400, JOINED_AFTER_LEAVING)
    stay.starts_on = joined_on


def update_me(
    session: Session, membership: Membership, data: MeUpdateIn, now: datetime
) -> Membership:
    """Fix your own name, and finish the first log-in check (FR-86).

    The room and join date stay with the owner and managers.

    Args:
        session: The database session.
        membership: The logged-in member.
        data: Their name.
        now: The current time.

    Returns:
        The changed membership.

    Raises:
        HTTPException: 409 for a name another active member has.
    """
    check_name_free(session, membership.home_id, data.name, except_id=membership.id)
    if data.name != membership.name:
        record_member_change(
            session,
            membership,
            changed_by=membership,
            action=ChangeAction.UPDATE,
            old_values={"name": membership.name},
            new_values={"name": data.name},
        )
    membership.name = data.name
    membership.details_checked_at = now
    session.commit()
    session.refresh(membership)
    return membership


def record_member_change(
    session: Session,
    member: Membership,
    *,
    changed_by: Membership,
    action: ChangeAction,
    old_values: dict[str, Any] | None = None,
    new_values: dict[str, Any] | None = None,
) -> None:
    """Keep a change to ``member`` in the history (FR-27), not yet committed.

    Args:
        session: The database session the change is made in.
        member: The member changed.
        changed_by: Who changed it.
        action: Created or updated.
        old_values: The changed fields before.
        new_values: The changed fields after.
    """
    history.record_change(
        session,
        home_id=member.home_id,
        changed_by=changed_by.id,
        entity=ChangeEntity.MEMBERSHIP,
        entity_id=member.id,
        action=action,
        old_values=old_values,
        new_values=new_values,
    )


def change_role(
    session: Session,
    owner: Membership,
    member_id: uuid.UUID,
    data: RoleIn,
    now: datetime,
) -> Membership:
    """Give or take away the Manager role (FR-62, FR-63), for the owner only.

    Args:
        session: The database session.
        owner: The home's owner.
        member_id: The member whose role changes.
        data: Their new role, member or manager.
        now: The current time.

    Returns:
        The changed membership.

    Raises:
        HTTPException: 404 for another home's member; 400 for the owner,
            whose role never changes.
    """
    member = get_member(session, owner.home_id, member_id)
    if member.role == Role.OWNER:
        raise HTTPException(400, OWNER_ROLE_FIXED)
    if member.role != data.role:
        record_member_change(
            session,
            member,
            changed_by=owner,
            action=ChangeAction.UPDATE,
            old_values={"role": member.role},
            new_values={"role": data.role},
        )
        member.role = data.role
    session.commit()
    session.refresh(member)
    return member
