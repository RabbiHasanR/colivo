from fastapi import Request, Response

from app.api.deps import CurrentMemberDep
from app.core.clock import ClockDep
from app.core.database import SessionDep
from app.core.notifier import NotifierDep
from app.core.redis import RedisDep
from app.core.router import CoreRouter
from app.core.utils import set_response_message
from app.modules.accounts import service, sessions
from app.modules.accounts.constants import SESSION_COOKIE
from app.modules.accounts.schemas import (
    CodeRequestIn,
    CodeSentOut,
    MeOut,
    SignUpIn,
)

router = CoreRouter()


@router.post("/auth/codes")
def request_code(
    request: Request,
    response: Response,
    data: CodeRequestIn,
    redis_client: RedisDep,
    notifier: NotifierDep,
    clock: ClockDep,
) -> CodeSentOut:
    """Send a one-time code by SMS or email; the same answer for any contact."""
    sent = service.request_code(redis_client, notifier, data.contact, clock())
    set_response_message(request, "Code sent")
    response.status_code = 200
    return sent


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


@router.post("/auth/log-out")
def log_out(request: Request, response: Response, membership: CurrentMemberDep) -> None:
    """End the session and clear its cookie."""
    set_response_message(request, "Logged out")
    response.status_code = 200


@router.get("/me")
def get_me(
    request: Request,
    response: Response,
    membership: CurrentMemberDep,
    session: SessionDep,
) -> MeOut:
    """Who is logged in, and in which home."""
    set_response_message(request, "Logged in")
    response.status_code = 200
    return service.get_me(session, membership)
