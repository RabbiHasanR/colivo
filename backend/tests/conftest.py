"""Shared test setup (specs/testing.md → Backend).

The test database is rebuilt once per run with ``alembic upgrade head``, so
every run also checks the migrations. Each test then runs in a transaction
that is rolled back, so tests never see each other's data.
"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import Engine, make_url, text
from sqlmodel import Session, create_engine

from app.core.config import settings
from app.core.database import get_session
from app.main import app

ALEMBIC_INI = Path(__file__).resolve().parents[1] / "alembic.ini"


def resolve_test_database_url() -> str:
    """Return TEST_DATABASE_URL, refusing to run against the app's own database."""
    url = settings.test_database_url
    if not url:
        pytest.exit("TEST_DATABASE_URL is not set (see .env.example).", returncode=2)
    if make_url(url).database == make_url(settings.database_url).database:
        pytest.exit("TEST_DATABASE_URL must not be the app's database.", returncode=2)
    return url


@pytest.fixture(scope="session")
def engine() -> Iterator[Engine]:
    """An engine on a test database freshly built with ``alembic upgrade head``."""
    test_engine = create_engine(resolve_test_database_url(), pool_pre_ping=True)
    with test_engine.begin() as connection:
        # Start from an empty schema so edited migrations on a branch run again.
        connection.execute(text("DROP SCHEMA public CASCADE"))
        connection.execute(text("CREATE SCHEMA public"))
        alembic_config = Config(str(ALEMBIC_INI))
        alembic_config.attributes["connection"] = connection
        command.upgrade(alembic_config, "head")
    yield test_engine
    test_engine.dispose()


@pytest.fixture
def session(engine: Engine) -> Iterator[Session]:
    """A session whose work, commits included, is rolled back after the test."""
    connection = engine.connect()
    outer = connection.begin()
    test_session = Session(bind=connection, join_transaction_mode="create_savepoint")
    yield test_session
    test_session.close()
    outer.rollback()
    connection.close()


@pytest.fixture
def client(session: Session) -> Iterator[TestClient]:
    """A ``TestClient`` whose requests use the test's rolled-back session."""
    app.dependency_overrides[get_session] = lambda: session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
