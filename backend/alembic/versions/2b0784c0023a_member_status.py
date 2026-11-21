"""member status

Revision ID: 2b0784c0023a
Revises: d0fcb4a7b7ad
Create Date: 2026-11-21 22:15:31.222610

"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel  # noqa: F401  (autogenerate writes sqlmodel.sql.sqltypes.AutoString)
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2b0784c0023a"
down_revision: str | Sequence[str] | None = "d0fcb4a7b7ad"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Exactly one owner per home (FR-63).
    op.create_index(
        "uq_membership_one_owner",
        "membership",
        ["home_id"],
        unique=True,
        postgresql_where=sa.text("role = 'owner'"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("uq_membership_one_owner", table_name="membership")
