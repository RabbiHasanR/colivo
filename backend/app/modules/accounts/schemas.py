import uuid
from datetime import date

from pydantic import BaseModel

from app.core.schemas import ShortText
from app.modules.accounts.contact import ContactIn
from app.modules.accounts.models import MembershipStatus, Role


class SignUpIn(BaseModel):
    """The owner's sign-up: who they are, their code and their new home."""

    contact: ContactIn
    code: str
    name: ShortText
    home_name: ShortText
    area: ShortText | None = None
    first_month: date
    lives_here: bool


class MePersonOut(BaseModel):
    """The logged-in person's log-in identity."""

    phone: str | None


class MeMembershipOut(BaseModel):
    """The logged-in person's membership of their home."""

    id: uuid.UUID
    name: str
    role: Role
    status: MembershipStatus


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
