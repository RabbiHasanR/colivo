from datetime import date

from sqlalchemy import CheckConstraint, Text
from sqlmodel import Field

from app.core.models import TableBase, short_text_check


class Home(TableBase, table=True):
    """A shared home: the tenant every home-owned table points to."""

    __table_args__ = (
        short_text_check("name"),
        short_text_check("area", optional=True),
        CheckConstraint("extract(day FROM first_month) = 1", name="first_month"),
    )

    name: str = Field(sa_type=Text)  # pyright: ignore[reportArgumentType]
    area: str | None = Field(default=None, sa_type=Text)  # pyright: ignore[reportArgumentType]
    first_month: date
