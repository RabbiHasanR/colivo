from datetime import date

from sqlalchemy import CheckConstraint, Text, UniqueConstraint
from sqlmodel import Field

from app.core.models import TableBase, short_text_check
from app.modules.homes.constants import DEFAULT_TIME_ZONE


class Home(TableBase, table=True):
    """A shared home: the tenant every home-owned table points to."""

    __table_args__ = (
        UniqueConstraint("code"),
        CheckConstraint("code ~ '^[A-Z]{2}-[0-9]{4}$'", name="code"),
        short_text_check("name"),
        short_text_check("area", optional=True),
        CheckConstraint("extract(day FROM first_month) = 1", name="first_month"),
    )

    code: str = Field(sa_type=Text)  # pyright: ignore[reportArgumentType]
    name: str = Field(sa_type=Text)  # pyright: ignore[reportArgumentType]
    area: str | None = Field(default=None, sa_type=Text)  # pyright: ignore[reportArgumentType]
    first_month: date
    time_zone: str = Field(
        default=DEFAULT_TIME_ZONE,
        sa_type=Text,  # pyright: ignore[reportArgumentType]
        sa_column_kwargs={"server_default": DEFAULT_TIME_ZONE},
    )
