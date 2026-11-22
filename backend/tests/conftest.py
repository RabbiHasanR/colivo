"""Shared test setup (specs/testing.md → Backend).

The test database is rebuilt once per run with ``alembic upgrade head``, so
every run also checks the migrations. Each test then runs in a transaction
that is rolled back, so tests never see each other's data.
"""

import re
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from redis import Redis
from sqlalchemy import Engine, make_url, text
from sqlmodel import Session, create_engine

from app.core.clock import get_clock
from app.core.config import settings
from app.core.database import get_session
from app.core.notifier import Channel, get_notifier
from app.core.redis import create_redis_client, get_redis
from app.main import app

ALEMBIC_INI = Path(__file__).resolve().parents[1] / "alembic.ini"
# The test Redis database when TEST_REDIS_URL is unset.
DEFAULT_TEST_REDIS_DB = 15
# Every test starts at this moment unless it moves the clock:
# 21 Nov 2026, 16:00 in Dhaka.
TEST_NOW = datetime(2026, 11, 21, 10, 0, tzinfo=UTC)
CODE_PATTERN = re.compile(r"\b(\d{6})\b")


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


def resolve_test_redis_url() -> str:
    """Return TEST_REDIS_URL, or database 15 of REDIS_URL's server.

    Refuses to run against the app's own Redis database, whose sessions and
    codes the tests would otherwise wipe.
    """
    url = settings.test_redis_url
    if not url:
        base = settings.redis_url.rsplit("/", 1)[0]
        url = f"{base}/{DEFAULT_TEST_REDIS_DB}"
    if url.rstrip("/") == settings.redis_url.rstrip("/"):
        pytest.exit("TEST_REDIS_URL must not be the app's Redis.", returncode=2)
    return url


@pytest.fixture(scope="session")
def redis_server() -> Iterator[Redis]:
    """One client on the test Redis database for the whole run."""
    test_client = create_redis_client(resolve_test_redis_url())
    yield test_client
    test_client.close()


@pytest.fixture
def redis_client(redis_server: Redis) -> Iterator[Redis]:
    """The test Redis database, emptied after each test."""
    yield redis_server
    redis_server.flushdb()


@dataclass
class SentMessage:
    """One message the app sent."""

    channel: Channel
    to: str
    text: str


@dataclass
class FakeNotifier:
    """Collects messages instead of sending them (SMS and email are external)."""

    sent: list[SentMessage] = field(default_factory=list)

    def send(self, channel: Channel, to: str, text: str) -> None:
        """Record the message."""
        self.sent.append(SentMessage(channel, to, text))

    def last_code_to(self, to: str) -> str:
        """Return the six-digit code in the last message sent to ``to``."""
        for message in reversed(self.sent):
            match = CODE_PATTERN.search(message.text)
            if message.to == to and match:
                return match.group(1)
        raise AssertionError(f"No code was sent to {to}")


@pytest.fixture
def notifier() -> FakeNotifier:
    """The notifier the app uses in this test."""
    return FakeNotifier()


@dataclass
class MovableClock:
    """A clock tests can move: ``clock.advance(timedelta(minutes=6))``."""

    now: datetime = TEST_NOW

    def __call__(self) -> datetime:
        """Return the current test time."""
        return self.now

    def advance(self, delta: timedelta) -> None:
        """Move the clock forward by ``delta``."""
        self.now += delta


@pytest.fixture
def clock() -> MovableClock:
    """The clock the app uses in this test, starting at ``TEST_NOW``."""
    return MovableClock()


@pytest.fixture
def client(
    session: Session,
    redis_client: Redis,
    notifier: FakeNotifier,
    clock: MovableClock,
) -> Iterator[TestClient]:
    """A ``TestClient`` on the test's database, Redis, notifier and clock.

    HTTPS, so ``Secure`` cookies are sent back like in a browser.
    """
    app.dependency_overrides[get_session] = lambda: session
    app.dependency_overrides[get_redis] = lambda: redis_client
    app.dependency_overrides[get_notifier] = lambda: notifier
    app.dependency_overrides[get_clock] = lambda: clock
    with TestClient(app, base_url="https://testserver") as test_client:
        yield test_client
    app.dependency_overrides.clear()
