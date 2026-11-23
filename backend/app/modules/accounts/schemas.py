import uuid
from datetime import date
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel

from app.core.notifier import Channel
from app.core.schemas import ShortText
from app.modules.accounts.contact import ContactIn
from app.modules.accounts.models import MembershipStatus, Role


class CodeErrorReason(StrEnum):
    """Why a one-time code, or a new one, was refused (FR-94)."""

    WRONG = "wrong"
    EXPIRED = "expired"
    LOCKED = "locked"
    TOO_SOON = "too_soon"
    HOURLY_LIMIT = "hourly_limit"


class CodeErrorOut(BaseModel):
    """The ``data`` of a refused code: why, and what the person can do next."""

    reason: CodeErrorReason
    tries_left: int | None = None
    retry_in_seconds: int | None = None


class CodeRequestIn(BaseModel):
    """Ask for a one-time code for a phone or email."""

    contact: ContactIn


class CodeSentOut(BaseModel):
    """How the code was sent and how long it works; the same for any contact."""

    channel: Channel
    expires_in_seconds: int
    resend_in_seconds: int


class LogInIn(BaseModel):
    """Log in with a phone or email and the code sent to it."""

    contact: ContactIn
    code: str


class SignUpIn(BaseModel):
    """The owner's sign-up: who they are, their code and their new home."""

    contact: ContactIn
    code: str
    name: ShortText
    home_name: ShortText
    area: ShortText | None = None
    first_month: date
    lives_here: bool


class MemberIn(BaseModel):
    """Add a member: who, how to reach them, from when, and their role."""

    name: ShortText
    contact: ContactIn
    joined_on: date
    role: Literal[Role.MEMBER, Role.MANAGER] = Role.MEMBER


class MemberUpdateIn(BaseModel):
    """Change a member's name or join date; leave out what stays the same."""

    name: ShortText | None = None
    joined_on: date | None = None


class MeUpdateIn(BaseModel):
    """Fix your own name; sending it also finishes the first log-in check."""

    name: ShortText


class RoleIn(BaseModel):
    """Give or take away the Manager role; the owner's role never changes."""

    role: Literal[Role.MEMBER, Role.MANAGER]


class DeactivateIn(BaseModel):
    """Deactivate a member from a date: today or earlier (FR-92)."""

    on: date
    reason: str | None = None


class ReactivateIn(BaseModel):
    """Reactivate a member from the date charges start again (FR-92)."""

    on: date


class MemberOut(BaseModel):
    """A member of the home, for the owner and managers' members list."""

    id: uuid.UUID
    name: str
    phone: str | None
    email: str | None
    role: Role
    status: MembershipStatus
    joined_on: date | None


class MePersonOut(BaseModel):
    """The logged-in person's log-in identity."""

    phone: str | None


class MeMembershipOut(BaseModel):
    """The logged-in person's membership of their home."""

    id: uuid.UUID
    name: str
    role: Role
    status: MembershipStatus
    joined_on: date | None = None
    # Who added them ("Added by Rabbi Hasan"); None for the owner.
    added_by_name: str | None = None
    # Whether the first log-in check is done (FR-86).
    details_checked: bool = False


class MeHomeOut(BaseModel):
    """The logged-in person's home."""

    id: uuid.UUID
    code: str
    name: str
    area: str | None
    first_month: date


class MeOut(BaseModel):
    """Who is logged in, and in which home."""

    person: MePersonOut
    membership: MeMembershipOut
    home: MeHomeOut


class HomeChoiceOut(BaseModel):
    """One of the person's active homes, for choosing or switching homes."""

    id: uuid.UUID
    name: str
    area: str | None
    # The person's role in that home.
    role: Role


class LogInOut(BaseModel):
    """The answer to a log-in: the person's homes, and ``me`` for one home.

    With several homes, ``me`` is None and the client asks which home.
    """

    homes: list[HomeChoiceOut]
    me: MeOut | None = None
