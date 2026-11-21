from typing import Annotated

from fastapi import Depends, Request
from starlette.exceptions import HTTPException

from app.core.clock import ClockDep
from app.core.database import SessionDep
from app.core.redis import RedisDep
from app.modules.accounts import service, sessions
from app.modules.accounts.constants import SESSION_COOKIE
from app.modules.accounts.models import Membership, Person

NOT_LOGGED_IN = "Log in first."


def current_membership(
    request: Request, session: SessionDep, redis_client: RedisDep, clock: ClockDep
) -> Membership:
    """Return the logged-in person's active membership (a FastAPI dependency).

    The membership is read from the database on every request, so a member
    who is deactivated is logged out at once (FR-80).

    Args:
        request: The request, carrying the session cookie.
        session: The database session.
        redis_client: Where sessions are kept.
        clock: The app's clock.

    Returns:
        The active membership.

    Raises:
        HTTPException: 401 without a live session or an active membership.
    """
    token = request.cookies.get(SESSION_COOKIE)
    person_id = token and sessions.read_session(redis_client, token, clock())
    person = person_id and session.get(Person, person_id)
    membership = person and service.active_membership(session, person)
    if not membership:
        raise HTTPException(401, NOT_LOGGED_IN)
    return membership


# The logged-in member for an endpoint: `membership: CurrentMemberDep`.
CurrentMemberDep = Annotated[Membership, Depends(current_membership)]
