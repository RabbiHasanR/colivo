import uuid
from datetime import date
from enum import StrEnum

from sqlalchemy import Text
from sqlmodel import Field

from app.core.models import TableBase, check_in, short_text_check


class Role(StrEnum):
    """A member's role in their home (specs/data-model.md → Roles)."""

    OWNER = "owner"
    MANAGER = "manager"
    MEMBER = "member"


class MembershipStatus(StrEnum):
    """Whether a member may log in now."""

    ACTIVE = "active"
    INACTIVE = "inactive"


class Person(TableBase, table=True):
    """A log-in identity, shared across homes; nothing about life in a home."""

    phone: str | None = Field(default=None, sa_type=Text)  # pyright: ignore[reportArgumentType]


class Membership(TableBase, table=True):
    """A person in one home. Everything in a home points here, not to person."""

    __table_args__ = (
        short_text_check("name"),
        check_in("role", Role),
        check_in("status", MembershipStatus),
    )

    home_id: uuid.UUID = Field(foreign_key="home.id")
    person_id: uuid.UUID = Field(foreign_key="person.id")
    name: str = Field(sa_type=Text)  # pyright: ignore[reportArgumentType]
    role: Role = Field(default=Role.MEMBER, sa_type=Text)  # pyright: ignore[reportArgumentType]
    status: MembershipStatus = Field(
        default=MembershipStatus.ACTIVE,
        sa_type=Text,  # pyright: ignore[reportArgumentType]
    )


class MembershipPeriod(TableBase, table=True):
    """A stay: when a member lives in the home and is charged (FR-92)."""

    home_id: uuid.UUID = Field(foreign_key="home.id")
    membership_id: uuid.UUID = Field(foreign_key="membership.id")
    starts_on: date
    ends_on: date | None = None
