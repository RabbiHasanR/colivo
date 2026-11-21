import uuid

from fastapi import Request, Response
from starlette.exceptions import HTTPException

from app.api.deps import CurrentMemberDep, OwnerDep, OwnerOrManagerDep
from app.core.clock import ClockDep
from app.core.config import settings
from app.core.database import SessionDep
from app.core.notifier import NotifierDep
from app.core.redis import RedisDep
from app.core.router import CoreRouter
from app.core.schemas import StandardResponse
from app.core.utils import set_response_message
from app.modules.accounts import service, sessions
from app.modules.accounts.constants import SESSION_COOKIE, SESSION_LIFETIME
from app.modules.accounts.models import Role
from app.modules.accounts.schemas import (
    CodeErrorOut,
    CodeRequestIn,
    CodeSentOut,
    LogInIn,
    MemberIn,
    MemberOut,
    MemberUpdateIn,
    MeOut,
    MeUpdateIn,
    RoleIn,
    SignUpIn,
)

router = CoreRouter()

# A refused one-time code: why, and what the person can do next.
CODE_ERRORS: dict[int | str, dict[str, object]] = {
    400: {"model": StandardResponse[CodeErrorOut]},
    429: {"model": StandardResponse[CodeErrorOut]},
}


def set_session_cookie(response: Response, token: str) -> None:
    """Send the session cookie, valid as long as the session (30 days).

    ``HttpOnly``: page scripts can't read it, so an XSS bug can't steal it.
    ``SameSite=Lax``: other sites can't send it with their forms (CSRF).
    ``Secure`` (on outside localhost): it travels over HTTPS only.

    Args:
        response: The response to set it on.
        token: The session token.
    """
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=int(SESSION_LIFETIME.total_seconds()),
        httponly=True,
        samesite="lax",
        secure=settings.session_cookie_secure,
    )


@router.post("/auth/codes", responses=CODE_ERRORS)
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


@router.post("/auth/sign-up", status_code=201, responses=CODE_ERRORS)
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
    set_session_cookie(response, token)
    set_response_message(request, "Home created")
    response.status_code = 201
    return service.get_me(session, membership)


@router.post("/auth/log-in", responses=CODE_ERRORS)
def log_in(
    request: Request,
    response: Response,
    data: LogInIn,
    session: SessionDep,
    redis_client: RedisDep,
    clock: ClockDep,
) -> MeOut:
    """Log in with a phone or email and its one-time code."""
    membership = service.log_in(session, redis_client, data, clock())
    token = sessions.create_session(redis_client, membership.person_id, clock())
    set_session_cookie(response, token)
    set_response_message(request, "Logged in")
    response.status_code = 200
    return service.get_me(session, membership)


@router.post("/auth/log-out")
def log_out(
    request: Request,
    response: Response,
    membership: CurrentMemberDep,
    redis_client: RedisDep,
) -> None:
    """End the session and clear its cookie."""
    service.log_out(redis_client, request.cookies[SESSION_COOKIE])
    response.delete_cookie(SESSION_COOKIE)
    set_response_message(request, "Logged out")
    response.status_code = 200


@router.get("/me")
def get_me(
    request: Request,
    response: Response,
    membership: CurrentMemberDep,
    session: SessionDep,
) -> MeOut:
    """Who is logged in, and in which home; renews the cookie for 30 days."""
    set_session_cookie(response, request.cookies[SESSION_COOKIE])
    set_response_message(request, "Logged in")
    response.status_code = 200
    return service.get_me(session, membership)


@router.get("/members")
def list_members(
    request: Request,
    response: Response,
    membership: OwnerOrManagerDep,
    session: SessionDep,
) -> list[MemberOut]:
    """Everyone in the home, for the owner and managers."""
    set_response_message(request, "Members")
    response.status_code = 200
    return service.list_members(session, membership.home_id)


@router.post("/members", status_code=201)
def add_member(
    request: Request,
    response: Response,
    data: MemberIn,
    adder: OwnerOrManagerDep,
    session: SessionDep,
    notifier: NotifierDep,
    clock: ClockDep,
) -> MemberOut:
    """Add a member to the home; they get an SMS or email to log in."""
    if data.role == Role.MANAGER and adder.role != Role.OWNER:
        # FR-64: only the owner makes managers.
        raise HTTPException(403, "Only the owner can add a manager.")
    member = service.add_member(session, notifier, adder, data, clock())
    set_response_message(request, "Member added")
    response.status_code = 201
    return service.member_out(session, member)


@router.patch("/members/{member_id}")
def update_member(
    request: Request,
    response: Response,
    member_id: uuid.UUID,
    data: MemberUpdateIn,
    editor: OwnerOrManagerDep,
    session: SessionDep,
    clock: ClockDep,
) -> MemberOut:
    """Change a member's name or join date."""
    member = service.update_member(session, editor, member_id, data, clock())
    set_response_message(request, "Member changed")
    response.status_code = 200
    return service.member_out(session, member)


@router.patch("/me")
def update_me(
    request: Request,
    response: Response,
    data: MeUpdateIn,
    membership: CurrentMemberDep,
    session: SessionDep,
    clock: ClockDep,
) -> MeOut:
    """Fix your own name; this also finishes the first log-in check."""
    changed = service.update_me(session, membership, data, clock())
    set_response_message(request, "Details checked")
    response.status_code = 200
    return service.get_me(session, changed)


@router.put("/members/{member_id}/role")
def change_role(
    request: Request,
    response: Response,
    member_id: uuid.UUID,
    data: RoleIn,
    owner: OwnerDep,
    session: SessionDep,
    clock: ClockDep,
) -> MemberOut:
    """Give or take away the Manager role; the owner only."""
    member = service.change_role(session, owner, member_id, data, clock())
    set_response_message(request, "Role changed")
    response.status_code = 200
    return service.member_out(session, member)
