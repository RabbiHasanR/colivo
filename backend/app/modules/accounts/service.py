import uuid
from datetime import date, datetime
from typing import Any
from zoneinfo import ZoneInfo

from redis import Redis
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, col, func, select
from starlette.exceptions import HTTPException

from app.core.exceptions import AppError
from app.core.notifier import Channel, Notifier
from app.modules.accounts import codes, sessions
from app.modules.accounts.constants import CODE_LIFETIME, CODE_RESEND_AFTER
from app.modules.accounts.contact import Contact, partly_hidden
from app.modules.accounts.models import (
    Membership,
    MembershipPeriod,
    MembershipStatus,
    Person,
    Role,
)
from app.modules.accounts.schemas import (
    CodeSentOut,
    ContactChangeIn,
    ContactKind,
    DeactivateIn,
    HomeChoiceOut,
    HomeRefusalOut,
    HomeRefusalReason,
    LogInIn,
    LogInOut,
    MeHomeOut,
    MemberIn,
    MemberOut,
    MemberUpdateIn,
    MeMembershipOut,
    MeOut,
    MePersonOut,
    MeUpdateIn,
    ReactivateIn,
    RoleIn,
    SignUpIn,
)
from app.modules.history import service as history
from app.modules.history.models import ChangeAction, ChangeEntity
from app.modules.homes import service as homes_service
from app.modules.homes.constants import DEFAULT_TIME_ZONE
from app.modules.homes.models import Home

ALREADY_IN_THIS_HOME = "Already a member of this home."
CHOOSE_HOME = "Choose a home."
NOT_IN_HOME = "You're no longer a member of this home."
PAST_MEMBER = "This person was a member of this home. Reactivate them instead."
NAME_TAKEN = "Someone in this home already has that name."
NO_STAY = "Only someone who lives in the home has a join date."
JOINED_AFTER_LEAVING = "The join date can't be after the end of their first stay."
MEMBER_NOT_FOUND = "Member not found."
OWNER_ROLE_FIXED = "The owner's role can't change."
DEACTIVATE_LATER = "Deactivation starts today or earlier."
ALREADY_INACTIVE = "This member is already deactivated."
OWNER_STAYS = "The owner can't be deactivated."
MANAGER_FOR_OWNER = "Only the owner can deactivate a manager."
REACTIVATE_MANAGER_FOR_OWNER = "Only the owner can reactivate a manager."
OWNER_DETAILS_FOR_OWNER = "Only the owner can change the owner's details."
REACTIVATE_TOO_EARLY = "Charges can start again only after their last stay ended."
ALREADY_ACTIVE = "This member is already active."
DEACTIVATE_BEFORE_STAY = "Deactivation can't start before their stay began."
LAST_CONTACT = "They need a phone or an email to log in."
CONTACT_TAKEN = "Someone else logs in with that phone or email."
SAME_CONTACT = "That's already their phone or email."
ONLY_THEY_CAN = "Only they can change their log-in, from My profile."
REACTIVATE_FIRST = "Reactivate them first."
# Told to a phone or email that no longer logs in.
CONTACT_REMOVED = (
    "This {kind} no longer logs in to your Colivo account. "
    "If this wasn't you, tell your home's owner or a manager."
)
# Told to a person's other phone or email when one is added or changed.
CONTACT_ADDED = (
    "{shown} can now log in to your Colivo account. "
    "If this wasn't you, tell your home's owner or a manager."
)
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


def membership_for(
    session: Session, person: Person, home_id: uuid.UUID | None
) -> Membership:
    """The person's active membership of the home a request names.

    A request that names no home acts in the person's only home; with
    several, it must say which (Phase 1b), so a missing header never sends
    a change to the wrong home.

    Args:
        session: The database session.
        person: The logged-in person.
        home_id: The home named in the ``X-Colivo-Home`` header, if any.

    Returns:
        The active membership.

    Raises:
        AppError: 409 "Choose a home." when no home is named and the person
            is active in several; 403 when the named home isn't one they are
            active in now, whether or not it exists.
        HTTPException: 401 when they are active in no home.
    """
    query = select(Membership).where(
        Membership.person_id == person.id,
        Membership.status == MembershipStatus.ACTIVE,
    )
    if home_id is not None:
        query = query.where(Membership.home_id == home_id)
    memberships = session.exec(query.limit(2)).all()
    if home_id is None and len(memberships) > 1:
        raise AppError(
            409, CHOOSE_HOME, HomeRefusalOut(reason=HomeRefusalReason.CHOOSE_HOME)
        )
    if not memberships and home_id is not None:
        # The same answer whether the home exists or not, so nobody learns
        # which homes exist.
        raise AppError(
            403, NOT_IN_HOME, HomeRefusalOut(reason=HomeRefusalReason.NOT_IN_HOME)
        )
    if not memberships:
        raise HTTPException(401, "Log in first.")
    return memberships[0]


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
        HTTPException: 400 for a first month that isn't this month or next.
    """
    # The first month says nothing about who someone is, so it is checked
    # before the code (a wrong month doesn't use the code up). Someone already
    # in other homes gets one more (Phase 1b).
    homes_service.check_first_month(data.first_month, now, DEFAULT_TIME_ZONE)
    codes.use_code(redis_client, data.contact, data.code, now)
    person = find_person(session, data.contact) or new_person(data.contact)
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
        homes=active_homes(session, person),
    )


def request_code(
    redis_client: Redis,
    notifier: Notifier,
    contact: Contact,
    now: datetime,
    scope: str = codes.LOG_IN_SCOPE,
) -> CodeSentOut:
    """Send a one-time code to ``contact`` by SMS or email (FR-94).

    The answer is the same whether or not anyone uses ``contact``, so nobody
    can find out who has an account.

    Args:
        redis_client: Where codes are kept.
        notifier: Sends the SMS or email.
        contact: The phone or email to send it to.
        now: The current time.
        scope: What the code is for: logging in, or one person's change.

    Returns:
        How it was sent, how long it works and when a new one can be sent.
    """
    code = codes.issue_code(redis_client, contact, now, scope)
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


def active_homes(session: Session, person: Person) -> list[HomeChoiceOut]:
    """The homes ``person`` is an active member of, by name, with their role.

    Args:
        session: The database session.
        person: The person.

    Returns:
        One row per active home; empty when they are active nowhere.
    """
    rows = session.exec(
        select(Home, Membership.role)
        .join(Membership, col(Membership.home_id) == col(Home.id))
        .where(
            Membership.person_id == person.id,
            Membership.status == MembershipStatus.ACTIVE,
        )
        .order_by(col(Home.name))
    ).all()
    return [
        HomeChoiceOut(id=home.id, name=home.name, area=home.area, role=Role(role))
        for home, role in rows
    ]


def log_in(
    session: Session, redis_client: Redis, data: LogInIn, now: datetime
) -> tuple[Person, LogInOut]:
    """Log in with a one-time code (FR-84).

    A person in one home goes straight to it; with several, the answer
    lists them and the client asks which one (Phase 1b).

    Args:
        session: The database session.
        redis_client: Where one-time codes are kept.
        data: The phone or email, and the code sent to it.
        now: The current time.

    Returns:
        The person, for the session, and the answer: their homes, and
        ``me`` when there is exactly one.

    Raises:
        HTTPException: 404 "Not added yet" when the person is active in no
            home: never added, or deactivated (FR-87).
    """
    codes.use_code(redis_client, data.contact, data.code, now)
    person = find_person(session, data.contact)
    homes = active_homes(session, person) if person else []
    if not person or not homes:
        # Only after the right code, so nobody learns who has an account.
        raise HTTPException(404, NOT_ADDED)
    me = None
    if len(homes) == 1:
        membership = membership_in(session, person, homes[0].id)
        me = membership and get_me(session, membership)
    return person, LogInOut(homes=homes, me=me)


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
        HTTPException: 409 when the person is already an active member of
            this home, was one (they are reactivated instead), or an active
            member already has the name. Being active in another home is
            fine (Phase 1b).
    """
    person = find_person(session, data.contact)
    existing = person and membership_in(session, person, adder.home_id)
    if existing:
        # One membership per person per home: an active one is a duplicate,
        # an inactive one is reactivated instead.
        active = existing.status == MembershipStatus.ACTIVE
        raise HTTPException(409, ALREADY_IN_THIS_HOME if active else PAST_MEMBER)
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


def member_out(
    session: Session, membership: Membership, viewer: Membership
) -> MemberOut:
    """Describe a member for the members list.

    Args:
        session: The database session.
        membership: The member.
        viewer: The owner or manager reading it, for ``contact_editable``.

    Returns:
        Their name, phone and email, role, status, join date, and whether
        ``viewer`` may change their log-in.
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
        contact_editable=contact_refusal(session, viewer, membership) is None,
    )


def list_members(session: Session, viewer: Membership) -> list[MemberOut]:
    """Everyone in the viewer's home, A to Z, for the owner and managers.

    Args:
        session: The database session.
        viewer: The owner or manager reading it.

    Returns:
        The members, active and deactivated.
    """
    members = session.exec(
        select(Membership)
        .where(Membership.home_id == viewer.home_id)
        .order_by(func.lower(Membership.name))
    ).all()
    return [member_out(session, member, viewer) for member in members]


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
        HTTPException: 404 for a member of another home; 403 for a manager
            changing the owner; 400 for a join date they can't have; 409 for
            a name an active member already has.
    """
    member = get_member(session, editor.home_id, member_id)
    if member.role == Role.OWNER and editor.role != Role.OWNER:
        raise HTTPException(403, OWNER_DETAILS_FOR_OWNER)
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
    session: Session,
    home_id: uuid.UUID,
    member_id: uuid.UUID,
    *,
    lock: bool = False,
) -> Membership:
    """A member of ``home_id``; another home's members are never found.

    Args:
        session: The database session.
        home_id: The home the request is for.
        member_id: The member asked for.
        lock: Lock their row until the commit (status changes), so two
            changes at the same moment can't both pass their checks.

    Returns:
        The membership.

    Raises:
        HTTPException: 404 for another home's member or an unknown id, so
            nobody learns another home's members exist (NFR-03).
    """
    query = select(Membership).where(Membership.id == member_id)
    if lock:
        query = query.with_for_update()
    member = session.exec(query).first()
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


def deactivate(
    session: Session,
    editor: Membership,
    member_id: uuid.UUID,
    data: DeactivateIn,
    now: datetime,
) -> Membership:
    """Deactivate a member from a date (FR-80, FR-92); they can't log in after.

    Their open stay ends on that date. The member's row is locked first.

    Args:
        session: The database session.
        editor: The owner or manager deactivating them.
        member_id: The member.
        data: The date it starts, and an optional reason.
        now: The current time.

    Returns:
        The deactivated membership.

    Raises:
        HTTPException: 404 for another home's member; 400 for the owner;
            403 for a manager deactivating a manager; 409 when already
            inactive; 400 for a date after today or before their stay began.
    """
    member = get_member(session, editor.home_id, member_id, lock=True)
    if member.role == Role.OWNER:
        raise HTTPException(400, OWNER_STAYS)
    if member.role == Role.MANAGER and editor.role != Role.OWNER:
        # A manager can't make managers (FR-64), so can't remove one either.
        raise HTTPException(403, MANAGER_FOR_OWNER)
    if member.status == MembershipStatus.INACTIVE:
        raise HTTPException(409, ALREADY_INACTIVE)
    if data.on > home_today(session, member.home_id, now):
        raise HTTPException(400, DEACTIVATE_LATER)
    stay = open_stay(session, member)
    if stay is not None and data.on < stay.starts_on:
        raise HTTPException(400, DEACTIVATE_BEFORE_STAY)
    if stay is not None:
        stay.ends_on = data.on
    record_member_change(
        session,
        member,
        changed_by=editor,
        action=ChangeAction.UPDATE,
        old_values={"status": member.status},
        new_values={"status": MembershipStatus.INACTIVE, "on": data.on.isoformat()},
    )
    member.status = MembershipStatus.INACTIVE
    session.commit()
    session.refresh(member)
    return member


def open_stay(session: Session, member: Membership) -> MembershipPeriod | None:
    """The member's current stay, the one with no end yet.

    Args:
        session: The database session.
        member: The member.

    Returns:
        The stay, or None when they have none open.
    """
    return session.exec(
        select(MembershipPeriod).where(
            MembershipPeriod.membership_id == member.id,
            col(MembershipPeriod.ends_on).is_(None),
        )
    ).first()


def home_today(session: Session, home_id: uuid.UUID, now: datetime) -> date:
    """Today's date where the home is (NFR-10), not on the server.

    Args:
        session: The database session.
        home_id: The home.
        now: The current time.

    Returns:
        The date in the home's time zone.
    """
    home = session.get_one(Home, home_id)
    return now.astimezone(ZoneInfo(home.time_zone)).date()


def reactivate(
    session: Session,
    editor: Membership,
    member_id: uuid.UUID,
    data: ReactivateIn,
    now: datetime,
) -> Membership:
    """Reactivate a member from the date charges start again (FR-92).

    A new stay opens on that date; the old ones are kept. The member's row is
    locked first.

    Args:
        session: The database session.
        editor: The owner or manager reactivating them.
        member_id: The member.
        data: The date charges start again.
        now: The current time.

    Returns:
        The reactivated membership.

    Raises:
        HTTPException: 404 for another home's member; 403 for a manager
            reactivating a manager; 409 when already active, or an active
            member has their name; 400 for a date not after their last stay
            ended.
    """
    member = get_member(session, editor.home_id, member_id, lock=True)
    if member.role == Role.MANAGER and editor.role != Role.OWNER:
        # Bringing a manager back is the owner's call, as removing one is.
        raise HTTPException(403, REACTIVATE_MANAGER_FOR_OWNER)
    if member.status == MembershipStatus.ACTIVE:
        raise HTTPException(409, ALREADY_ACTIVE)
    last_end = last_stay_end(session, member)
    if last_end is not None and data.on <= last_end:
        raise HTTPException(400, REACTIVATE_TOO_EARLY)
    # Joining another home meanwhile is fine (Phase 1b); only the name must
    # still be free here.
    check_name_free(session, member.home_id, member.name, except_id=member.id)
    session.add(
        MembershipPeriod(
            home_id=member.home_id, membership_id=member.id, starts_on=data.on
        )
    )
    record_member_change(
        session,
        member,
        changed_by=editor,
        action=ChangeAction.UPDATE,
        old_values={"status": member.status},
        new_values={"status": MembershipStatus.ACTIVE, "on": data.on.isoformat()},
    )
    member.status = MembershipStatus.ACTIVE
    session.commit()
    session.refresh(member)
    return member


def last_stay_end(session: Session, member: Membership) -> date | None:
    """The day the member's latest stay ended, if any stay ended.

    Args:
        session: The database session.
        member: The member.

    Returns:
        The date, or None when no stay has ended.
    """
    return session.exec(
        select(func.max(MembershipPeriod.ends_on)).where(
            MembershipPeriod.membership_id == member.id
        )
    ).one()


# Phase 1c: the phone or email a person logs in with.


def kind_of(contact: Contact) -> ContactKind:
    """Whether ``contact`` is a phone or an email; also its ``person`` column."""
    return ContactKind.EMAIL if contact.channel == Channel.EMAIL else ContactKind.PHONE


def contacts_of(person: Person) -> list[Contact]:
    """The phone and email ``person`` logs in with now."""
    found = [Contact(channel=Channel.SMS, value=person.phone)] if person.phone else []
    if person.email:
        found.append(Contact(channel=Channel.EMAIL, value=person.email))
    return found


def record_log_in_change(
    session: Session,
    person: Person,
    changed_by: Membership | None,
    old_values: dict[str, Any],
    new_values: dict[str, Any],
) -> None:
    """Keep a change to ``person``'s log-in in every home they are in (FR-27).

    A log-in is the same in every home, so each home keeps its own proof,
    under the person's membership there. The editor is named in their own
    home; elsewhere (and for the person's own change) the person is.

    Args:
        session: The database session the change is made in.
        person: Whose log-in changed.
        changed_by: The owner or manager who changed it; None for the person.
        old_values: The phone or email before, e.g. ``{"email": None}``.
        new_values: The phone or email after.
    """
    memberships = session.exec(
        select(Membership).where(Membership.person_id == person.id)
    ).all()
    for member in memberships:
        editor_here = changed_by is not None and changed_by.home_id == member.home_id
        record_member_change(
            session,
            member,
            changed_by=changed_by if changed_by and editor_here else member,
            action=ChangeAction.UPDATE,
            old_values=old_values,
            new_values=new_values,
        )


def other_kind(kind: ContactKind) -> ContactKind:
    """The other way to log in: the email for a phone, the phone for an email."""
    return ContactKind.PHONE if kind == ContactKind.EMAIL else ContactKind.EMAIL


def request_contact_code(
    redis_client: Redis,
    notifier: Notifier,
    person: Person,
    contact: Contact,
    now: datetime,
) -> CodeSentOut:
    """Send a code to a new phone or email for ``person`` to log in with.

    Args:
        redis_client: Where codes are kept.
        notifier: Sends the SMS or email.
        person: Whose log-in changes.
        contact: The new phone or email.
        now: The current time.

    Returns:
        How the code was sent, how long it works and when a new one can be
        sent.

    Raises:
        HTTPException: 400 when it is the one they already have.
    """
    if getattr(person, kind_of(contact)) == contact.value:
        raise HTTPException(400, SAME_CONTACT)
    scope = codes.change_scope(person.id)
    return request_code(redis_client, notifier, contact, now, scope)


def set_contact(
    session: Session,
    redis_client: Redis,
    notifier: Notifier,
    person: Person,
    data: ContactChangeIn,
    now: datetime,
    *,
    changed_by: Membership | None = None,
    keep_token: str | None = None,
) -> Person:
    """Save a new phone or email for ``person``, with the code sent to it.

    A phone replaces their phone and an email their email.

    Args:
        session: The database session.
        redis_client: Where codes and sessions are kept.
        notifier: Tells the person on their old and new phone or email.
        person: Whose log-in changes.
        data: The new phone or email and its code.
        now: The current time.
        changed_by: The owner or manager making it; None for the person.
        keep_token: The caller's session, kept when theirs ends.

    Returns:
        The changed person.

    Raises:
        HTTPException: 409 when someone else logs in with it; checked only
            after the right code, so nobody learns who has an account.
    """
    scope = codes.change_scope(person.id)
    codes.use_code(redis_client, data.contact, data.code, now, scope)
    holder = find_person(session, data.contact)
    if holder is not None and holder.id != person.id:
        raise HTTPException(409, CONTACT_TAKEN)
    kind = kind_of(data.contact)
    before = contacts_of(person)
    old_value = getattr(person, kind)
    try:
        setattr(person, kind, data.contact.value)
        record_log_in_change(
            session, person, changed_by, {kind: old_value}, {kind: data.contact.value}
        )
        session.commit()
    except IntegrityError as error:
        # Taken by someone else after the check above: the unique index decides.
        session.rollback()
        raise HTTPException(409, CONTACT_TAKEN) from error
    session.refresh(person)
    if old_value is not None:
        # A way to log in was taken away: every other browser logs in again.
        sessions.end_sessions(redis_client, person.id, keep_token)
    added = CONTACT_ADDED.format(shown=partly_hidden(data.contact))
    for old in before:
        notifier.send(old.channel, old.value, added)
    notifier.send(
        data.contact.channel,
        data.contact.value,
        f"You can now log in to Colivo with this {kind}.",
    )
    return person


def in_another_home(session: Session, member: Membership) -> bool:
    """Whether ``member``'s person is also a member of another home.

    Args:
        session: The database session.
        member: The member.

    Returns:
        True when they have a membership in another home, active or past:
        a past one can be reactivated, and would then log in with it.
    """
    other = session.exec(
        select(Membership.id).where(
            Membership.person_id == member.person_id,
            Membership.home_id != member.home_id,
        )
    ).first()
    return other is not None


def contact_refusal(
    session: Session, editor: Membership, member: Membership
) -> HTTPException | None:
    """Why ``editor`` may not change ``member``'s log-in, or None if they may.

    A log-in belongs to the person in every home, so for someone also in
    another home only they may change it; otherwise one home's owner could
    take over their log-in everywhere.

    Args:
        session: The database session.
        editor: The owner or manager.
        member: The member whose log-in would change.

    Returns:
        The refusal to raise, or None.
    """
    if member.status != MembershipStatus.ACTIVE:
        return HTTPException(400, REACTIVATE_FIRST)
    if member.role == Role.OWNER and editor.role != Role.OWNER:
        return HTTPException(403, OWNER_DETAILS_FOR_OWNER)
    yourself = editor.person_id == member.person_id
    if not yourself and in_another_home(session, member):
        return HTTPException(403, ONLY_THEY_CAN)
    return None


def member_to_change(
    session: Session, editor: Membership, member_id: uuid.UUID
) -> tuple[Membership, Person]:
    """The member whose log-in ``editor`` changes, and their person.

    Args:
        session: The database session.
        editor: The owner or manager.
        member_id: The member asked for.

    Returns:
        The member and the person behind them.

    Raises:
        HTTPException: 404 for another home's member; the refusal from
            ``contact_refusal``.
    """
    member = get_member(session, editor.home_id, member_id)
    refusal = contact_refusal(session, editor, member)
    if refusal is not None:
        raise refusal
    return member, session.get_one(Person, member.person_id)


def request_member_contact_code(
    session: Session,
    redis_client: Redis,
    notifier: Notifier,
    editor: Membership,
    member_id: uuid.UUID,
    contact: Contact,
    now: datetime,
) -> CodeSentOut:
    """Send a code to a member's new phone or email, for the owner or a manager.

    Args:
        session: The database session.
        redis_client: Where codes are kept.
        notifier: Sends the SMS or email.
        editor: The owner or manager making the change.
        member_id: The member whose log-in changes.
        contact: The new phone or email.
        now: The current time.

    Returns:
        How the code was sent.
    """
    _, person = member_to_change(session, editor, member_id)
    return request_contact_code(redis_client, notifier, person, contact, now)


def set_member_contact(
    session: Session,
    redis_client: Redis,
    notifier: Notifier,
    editor: Membership,
    member_id: uuid.UUID,
    data: ContactChangeIn,
    now: datetime,
    *,
    keep_token: str | None = None,
) -> Membership:
    """Save a member's new phone or email with its code (owner or manager).

    Args:
        session: The database session.
        redis_client: Where codes are kept.
        notifier: Sends the notices.
        editor: The owner or manager making the change.
        member_id: The member whose log-in changes.
        data: The new phone or email and its code.
        now: The current time.
        keep_token: The editor's session, kept if they change their own row.

    Returns:
        The member.
    """
    member, person = member_to_change(session, editor, member_id)
    set_contact(
        session,
        redis_client,
        notifier,
        person,
        data,
        now,
        changed_by=editor,
        keep_token=keep_token,
    )
    return member


def remove_contact(
    session: Session,
    redis_client: Redis,
    notifier: Notifier,
    person: Person,
    kind: ContactKind,
    *,
    changed_by: Membership | None = None,
    keep_token: str | None = None,
) -> Person:
    """Stop ``person`` logging in with their phone or their email.

    Their sessions end, except the caller's.

    Args:
        session: The database session.
        redis_client: Where sessions are kept.
        notifier: Tells the removed phone or email.
        person: Whose log-in changes.
        kind: Which one to remove.
        changed_by: The owner or manager removing it; None for the person.
        keep_token: The caller's session, kept when theirs ends.

    Returns:
        The changed person.

    Raises:
        HTTPException: 400 when they have none of that kind, or it is the last
            way they log in.
    """
    removed = getattr(person, kind)
    if removed is None:
        raise HTTPException(400, f"They have no {kind} to remove.")
    if getattr(person, other_kind(kind)) is None:
        raise HTTPException(400, LAST_CONTACT)
    setattr(person, kind, None)
    record_log_in_change(session, person, changed_by, {kind: removed}, {kind: None})
    session.commit()
    session.refresh(person)
    sessions.end_sessions(redis_client, person.id, keep_token)
    channel = Channel.EMAIL if kind == ContactKind.EMAIL else Channel.SMS
    notifier.send(channel, removed, CONTACT_REMOVED.format(kind=kind))
    return person


def remove_member_contact(
    session: Session,
    redis_client: Redis,
    notifier: Notifier,
    editor: Membership,
    member_id: uuid.UUID,
    kind: ContactKind,
    now: datetime,
    *,
    keep_token: str | None = None,
) -> Membership:
    """Remove a member's phone or email, for the owner or a manager.

    Args:
        session: The database session.
        redis_client: Where sessions are kept.
        notifier: Sends the notice.
        editor: The owner or manager making the change.
        member_id: The member whose log-in changes.
        kind: Which one to remove.
        now: The current time.
        keep_token: The editor's session, kept if they change their own row.

    Returns:
        The member.
    """
    member, person = member_to_change(session, editor, member_id)
    remove_contact(
        session,
        redis_client,
        notifier,
        person,
        kind,
        changed_by=editor,
        keep_token=keep_token,
    )
    return member
