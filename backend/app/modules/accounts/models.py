import uuid
from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Index,
    Text,
    UniqueConstraint,
    func,
    text,
)
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

    __table_args__ = (
        UniqueConstraint("phone"),
        UniqueConstraint("email"),
        CheckConstraint("phone IS NOT NULL OR email IS NOT NULL", name="contact"),
        CheckConstraint(r"phone ~ '^\+[1-9][0-9]{7,14}$'", name="phone"),
        CheckConstraint("email = lower(email)", name="email"),
    )

    phone: str | None = Field(default=None, sa_type=Text)  # pyright: ignore[reportArgumentType]
    email: str | None = Field(default=None, sa_type=Text)  # pyright: ignore[reportArgumentType]


class Membership(TableBase, table=True):
    """A person in one home. Everything in a home points here, not to person."""

    __table_args__ = (
        short_text_check("name"),
        check_in("role", Role),
        check_in("status", MembershipStatus),
        # One membership per person per home: a returning member is reactivated.
        UniqueConstraint("home_id", "person_id"),
        # Names unique among a home's active members, any letter case (FR-04).
        Index(
            "uq_membership_active_name",
            "home_id",
            func.lower(text("name")),
            unique=True,
            postgresql_where=text("status = 'active'"),
        ),
        # Exactly one owner per home (FR-63).
        Index(
            "uq_membership_one_owner",
            "home_id",
            unique=True,
            postgresql_where=text("role = 'owner'"),
        ),
        # One active home per person (FR-85).
        Index(
            "uq_membership_active_person_id",
            "person_id",
            unique=True,
            postgresql_where=text("status = 'active'"),
        ),
    )

    home_id: uuid.UUID = Field(foreign_key="home.id")
    person_id: uuid.UUID = Field(foreign_key="person.id")
    name: str = Field(sa_type=Text)  # pyright: ignore[reportArgumentType]
    role: Role = Field(default=Role.MEMBER, sa_type=Text)  # pyright: ignore[reportArgumentType]
    status: MembershipStatus = Field(
        default=MembershipStatus.ACTIVE,
        sa_type=Text,  # pyright: ignore[reportArgumentType]
    )
    # Who added them ("Added by Rabbi Hasan"); None for the owner.
    created_by: uuid.UUID | None = Field(default=None, foreign_key="membership.id")
    # The first log-in check (FR-86) is shown until this is set.
    details_checked_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),  # pyright: ignore[reportArgumentType]
    )


class MembershipPeriod(TableBase, table=True):
    """A stay: when a member lives in the home and is charged (FR-92)."""

    home_id: uuid.UUID = Field(foreign_key="home.id")
    membership_id: uuid.UUID = Field(foreign_key="membership.id")
    starts_on: date
    ends_on: date | None = None
