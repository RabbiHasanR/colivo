import re
import typing
from enum import StrEnum

from sqlalchemy import text
from sqlmodel import Session, SQLModel


def enum_columns() -> list[tuple[str, str, type[StrEnum]]]:
    """Every (table, column, enum) where a model types a column as a StrEnum."""
    found: list[tuple[str, str, type[StrEnum]]] = []
    for mapper in SQLModel._sa_registry.mappers:  # pyright: ignore[reportPrivateUsage]
        model = mapper.class_
        table = model.__table__.name
        for name, hint in typing.get_type_hints(model).items():
            if isinstance(hint, type) and issubclass(hint, StrEnum):
                found.append((table, name, hint))
    return found


def test_every_check_matches_its_enum(session: Session) -> None:
    """
    GIVEN every model column typed as a StrEnum (role, status, …)
    WHEN  the test database's CHECK constraints are read
    THEN  each such column has a check allowing exactly its enum's values
    """
    rows = session.connection().execute(
        text("SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint")
    )
    definitions = {name: definition for name, definition in rows}

    columns = enum_columns()

    assert columns, "no model column is typed as a StrEnum"
    for table, column, enum in columns:
        definition = definitions.get(f"ck_{table}_{column}")
        assert definition is not None, f"{table}.{column} has no CHECK"
        assert set(re.findall(r"'([^']*)'", definition)) == {
            member.value for member in enum
        }, f"{table}.{column}"
