from fastapi import Request, Response

from app.core.clock import ClockDep
from app.core.database import SessionDep
from app.core.redis import RedisDep
from app.core.router import CoreRouter
from app.core.utils import set_response_message
from app.modules.accounts import service, sessions
from app.modules.accounts.constants import SESSION_COOKIE
from app.modules.accounts.schemas import MeOut, SignUpIn

router = CoreRouter()


@router.post("/auth/sign-up", status_code=201)
def sign_up(
    request: Request,
    response: Response,
    data: SignUpIn,
    session: SessionDep,
    redis_client: RedisDep,
    clock: ClockDep,
) -> MeOut:
    """Create a home; the person signing up becomes its owner and is logged in."""
    membership = service.sign_up(session, redis_client, data, clock())
    token = sessions.create_session(redis_client, membership.person_id, clock())
    response.set_cookie(SESSION_COOKIE, token)
    set_response_message(request, "Home created")
    response.status_code = 201
    return service.get_me(session, membership)
