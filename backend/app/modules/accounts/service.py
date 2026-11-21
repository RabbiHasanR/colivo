from datetime import datetime

from redis import Redis
from sqlmodel import Session, select
from starlette.exceptions import HTTPException

from app.modules.accounts import codes
from app.modules.accounts.contact import Contact
from app.modules.accounts.models import (
    Membership,
    MembershipPeriod,
    MembershipStatus,
    Person,
    Role,
)
from app.modules.accounts.schemas import (
    MeHomeOut,
    MeMembershipOut,
    MeOut,
    MePersonOut,
    SignUpIn,
)
from app.modules.homes import service as homes_service
from app.modules.homes.constants import DEFAULT_TIME_ZONE
from app.modules.homes.models import Home


def find_person(session: Session, contact: Contact) -> Person | None:
    """Return the person who logs in with ``contact``, if anyone does.

    Args:
        session: The database session.
        contact: A phone or email.

    Returns:
        The person, or None.
    """
    return session.exec(select(Person).where(Person.phone == contact.value)).first()


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
    codes.use_code(redis_client, data.contact, data.code, now)
    homes_service.check_first_month(data.first_month, now, DEFAULT_TIME_ZONE)
    person = find_person(session, data.contact) or Person(phone=data.contact.value)
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
