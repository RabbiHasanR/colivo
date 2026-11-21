import uuid
from enum import StrEnum
from typing import Any

from sqlalchemy import Index, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field

from app.core.models import AppendOnlyBase, check_in


class ChangeEntity(StrEnum):
    """What kind of record was changed. Later phases add values."""

    MEMBERSHIP = "membership"
    MEMBERSHIP_PERIOD = "membership_period"


class ChangeAction(StrEnum):
    """How it changed; ``delete`` is the soft delete of Phase 8."""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class ChangeLog(AppendOnlyBase, table=True):
    """Proof of who changed what, and when (FR-27). Rows are never changed."""

    __table_args__ = (
        check_in("entity", ChangeEntity),
        check_in("action", ChangeAction),
        Index("ix_change_log_record", "home_id", "entity", "entity_id", "created_at"),
    )

    home_id: uuid.UUID = Field(foreign_key="home.id")
    changed_by: uuid.UUID | None = Field(default=None, foreign_key="membership.id")
    entity: ChangeEntity = Field(sa_type=Text)  # pyright: ignore[reportArgumentType]
    entity_id: uuid.UUID
    action: ChangeAction = Field(sa_type=Text)  # pyright: ignore[reportArgumentType]
    old_values: dict[str, Any] | None = Field(default=None, sa_type=JSONB)  # pyright: ignore[reportArgumentType]
    new_values: dict[str, Any] | None = Field(default=None, sa_type=JSONB)  # pyright: ignore[reportArgumentType]
    reason: str | None = Field(default=None, sa_type=Text)  # pyright: ignore[reportArgumentType]
