"""several homes

Revision ID: a8f729dfae84
Revises: 2b0784c0023a
Create Date: 2026-11-23 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a8f729dfae84"
down_revision: str | Sequence[str] | None = "2b0784c0023a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # A person can be active in several homes (Phase 1b replaces FR-85): the
    # unique index becomes a plain one for "this person's active homes".
    op.drop_index(
        "uq_membership_active_person_id",
        table_name="membership",
        postgresql_where=sa.text("status = 'active'"),
    )
    op.create_index(
        "ix_membership_active_person_id",
        "membership",
        ["person_id"],
        postgresql_where=sa.text("status = 'active'"),
    )


def downgrade() -> None:
    """Downgrade schema.

    Fails if someone is by then active in two homes; acceptable for a
    development or test database.
    """
    op.drop_index(
        "ix_membership_active_person_id",
        table_name="membership",
        postgresql_where=sa.text("status = 'active'"),
    )
    op.create_index(
        "uq_membership_active_person_id",
        "membership",
        ["person_id"],
        unique=True,
        postgresql_where=sa.text("status = 'active'"),
    )
