import uuid
from typing import Any

from sqlmodel import Session

from app.modules.history.models import ChangeAction, ChangeEntity, ChangeLog


def record_change(
    session: Session,
    *,
    home_id: uuid.UUID,
    changed_by: uuid.UUID | None,
    entity: ChangeEntity,
    entity_id: uuid.UUID,
    action: ChangeAction,
    old_values: dict[str, Any] | None = None,
    new_values: dict[str, Any] | None = None,
    reason: str | None = None,
) -> None:
    """Record a change in the history (FR-27), in the caller's transaction.

    Never commits: the change and its history row are saved together, or not
    at all.

    Args:
        session: The database session the change is made in.
        home_id: The home it belongs to.
        changed_by: Who made it; None for a change the system makes.
        entity: What kind of record changed.
        entity_id: Which record.
        action: Created, updated or (soft) deleted.
        old_values: The changed fields before, for an update or delete.
        new_values: The changed fields after, for a create or update.
        reason: Why, when one was given.
    """
    session.add(
        ChangeLog(
            home_id=home_id,
            changed_by=changed_by,
            entity=entity,
            entity_id=entity_id,
            action=action,
            old_values=old_values,
            new_values=new_values,
            reason=reason,
        )
    )
