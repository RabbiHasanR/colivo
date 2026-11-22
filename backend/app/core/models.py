import re
import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import CheckConstraint, DateTime, func
from sqlalchemy.orm import declared_attr
from sqlmodel import Field, SQLModel

from app.core.schemas import SHORT_TEXT_MAX

# Stable constraint names, so migrations and error messages can name them.
SQLModel.metadata.naming_convention = {
    "pk": "pk_%(table_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
}


def snake_case(name: str) -> str:
    """Turn a class name into a table name: ``MealEntry`` → ``meal_entry``.

    Args:
        name: A class name in PascalCase.

    Returns:
        The name in snake_case.
    """
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def check_in(column: str, values: type[StrEnum]) -> CheckConstraint:
    """A ``CHECK (column IN (…))`` allowing exactly the values of ``values``.

    Named ``ck_<table>_<column>`` by the naming convention. Fixed value sets
    are text plus this check (specs/data-model.md → Fixed value sets);
    ``tests/core/test_models.py`` keeps every check equal to its enum.

    Args:
        column: The column name.
        values: The ``StrEnum`` whose values the column may hold.

    Returns:
        The check constraint, for a model's ``__table_args__``.
    """
    allowed = ", ".join(f"'{member.value}'" for member in values)
    return CheckConstraint(f"{column} IN ({allowed})", name=column)


def short_text_check(column: str, *, optional: bool = False) -> CheckConstraint:
    """A ``CHECK`` that ``column`` holds 1 to 80 characters once trimmed.

    The database's copy of the API's ``ShortText`` rule.

    Args:
        column: The column name.
        optional: Whether the column may be null.

    Returns:
        The check constraint, for a model's ``__table_args__``.
    """
    rule = f"char_length(btrim({column})) BETWEEN 1 AND {SHORT_TEXT_MAX}"
    if optional:
        rule = f"{column} IS NULL OR {rule}"
    return CheckConstraint(rule, name=column)


class AppendOnlyBase(SQLModel):
    """The base of a table whose rows are never changed (``change_log``).

    A UUIDv7 ``id`` made in Python, ``created_at`` set by the database, and a
    singular snake_case table name (specs/data-model.md → Conventions).
    """

    # SQLAlchemy's declared_attr pattern; pyright reads it as an instance
    # variable overriding SQLModel's class variable.
    @declared_attr  # pyright: ignore[reportArgumentType]
    def __tablename__(cls) -> str:  # noqa: N805  # pyright: ignore[reportIncompatibleVariableOverride]
        """The table name: the class name in snake_case."""
        return snake_case(cls.__name__)

    id: uuid.UUID = Field(default_factory=uuid.uuid7, primary_key=True)
    created_at: datetime | None = Field(
        default=None,
        nullable=False,
        sa_type=DateTime(timezone=True),  # pyright: ignore[reportArgumentType]
        sa_column_kwargs={"server_default": func.now()},
    )


class TableBase(AppendOnlyBase):
    """The base of every other table: also an ``updated_at`` set by the database."""

    updated_at: datetime | None = Field(
        default=None,
        nullable=False,
        sa_type=DateTime(timezone=True),  # pyright: ignore[reportArgumentType]
        sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()},
    )
