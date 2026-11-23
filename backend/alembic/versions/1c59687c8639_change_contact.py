"""change contact

Revision ID: 1c59687c8639
Revises: a8f729dfae84
Create Date: 2026-11-23 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1c59687c8639"
down_revision: str | Sequence[str] | None = "a8f729dfae84"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # "Is this person in any other home, active or past?" (Phase 1c) needs
    # every membership; the full index also serves "their active homes".
    op.drop_index(
        "ix_membership_active_person_id",
        table_name="membership",
        postgresql_where=sa.text("status = 'active'"),
    )
    op.create_index("ix_membership_person_id", "membership", ["person_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_membership_person_id", table_name="membership")
    op.create_index(
        "ix_membership_active_person_id",
        "membership",
        ["person_id"],
        postgresql_where=sa.text("status = 'active'"),
    )
