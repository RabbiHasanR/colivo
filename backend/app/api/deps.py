import uuid
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, Header, Request
from starlette.exceptions import HTTPException

from app.core.clock import ClockDep
from app.core.database import SessionDep
from app.core.redis import RedisDep
from app.modules.accounts import service, sessions
from app.modules.accounts.constants import HOME_HEADER, SESSION_COOKIE
from app.modules.accounts.models import Membership, Person, Role

NOT_LOGGED_IN = "Log in first."
NOT_ALLOWED = "Your role can't do this."


def current_person(
    request: Request, session: SessionDep, redis_client: RedisDep, clock: ClockDep
) -> Person:
    """Return the logged-in person (a FastAPI dependency), whatever home.

    A person who is active in no home is logged out: they were deactivated
    from their last home (FR-80).

    Args:
        request: The request, carrying the session cookie.
        session: The database session.
        redis_client: Where sessions are kept.
        clock: The app's clock.

    Returns:
        The person.

    Raises:
        HTTPException: 401 without a live session or an active home.
    """
    token = request.cookies.get(SESSION_COOKIE)
    person_id = token and sessions.read_session(redis_client, token, clock())
    person = person_id and session.get(Person, person_id)
    if not person or not service.active_homes(session, person):
        raise HTTPException(401, NOT_LOGGED_IN)
    return person


# The logged-in person, for endpoints that need no home: `CurrentPersonDep`.
CurrentPersonDep = Annotated[Person, Depends(current_person)]


def current_membership(
    person: CurrentPersonDep,
    session: SessionDep,
    home_id: Annotated[uuid.UUID | None, Header(alias=HOME_HEADER)] = None,
) -> Membership:
    """Return the logged-in person's membership of the home they act in.

    The home comes from the ``X-Colivo-Home`` header (Phase 1b); it only
    chooses among the person's own homes. The membership is read from the
    database on every request, so a deactivated member is refused at once
    (FR-80).

    Args:
        person: The logged-in person.
        session: The database session.
        home_id: The home the request names, if any.

    Returns:
        The active membership.
    """
    return service.membership_for(session, person, home_id)


# The logged-in member for an endpoint: `membership: CurrentMemberDep`.
CurrentMemberDep = Annotated[Membership, Depends(current_membership)]


def require_role(*roles: Role) -> Callable[[Membership], Membership]:
    """Build a dependency that lets only members with one of ``roles`` in.

    Args:
        *roles: The roles allowed.

    Returns:
        A FastAPI dependency giving the logged-in membership, or 403.
    """

    def check_role(membership: CurrentMemberDep) -> Membership:
        """Return the membership if its role is allowed.

        Raises:
            HTTPException: 403 for any other role.
        """
        if membership.role not in roles:
            raise HTTPException(403, NOT_ALLOWED)
        return membership

    return check_role


# The logged-in owner or a manager: `membership: OwnerOrManagerDep`.
OwnerOrManagerDep = Annotated[
    Membership, Depends(require_role(Role.OWNER, Role.MANAGER))
]


# The logged-in owner: `membership: OwnerDep`.
OwnerDep = Annotated[Membership, Depends(require_role(Role.OWNER))]
