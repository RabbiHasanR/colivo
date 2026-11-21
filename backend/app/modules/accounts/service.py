from datetime import datetime

from redis import Redis
from sqlmodel import Session

from app.modules.accounts import codes
from app.modules.accounts.models import Membership, Person, Role
from app.modules.accounts.schemas import (
    MeHomeOut,
    MeMembershipOut,
    MeOut,
    MePersonOut,
    SignUpIn,
)
from app.modules.homes.models import Home


def sign_up(
    session: Session, redis_client: Redis, data: SignUpIn, now: datetime
) -> Membership:
    """Create a home and make the person signing up its owner (FR-83).

    The person, the home and the owner's membership are saved in one
    transaction.

    Args:
        session: The database session.
        redis_client: Where one-time codes are kept.
        data: The sign-up form, with the code sent to its contact.
        now: The current time.

    Returns:
        The owner's new membership.
    """
    codes.use_code(redis_client, data.contact, data.code, now)
    person = Person(phone=data.contact.value)
    home = Home(name=data.home_name, area=data.area, first_month=data.first_month)
    # No ORM relationships, so the session doesn't order inserts by foreign
    # key: flush the parents first.
    session.add_all([person, home])
    session.flush()
    membership = Membership(
        home_id=home.id, person_id=person.id, name=data.name, role=Role.OWNER
    )
    session.add(membership)
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
