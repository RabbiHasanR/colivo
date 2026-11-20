"""Unreachable dependencies for the health tests: real clients, no mocks."""

from collections.abc import Iterator

import pytest
from redis import Redis
from sqlalchemy import NullPool
from sqlmodel import Session, create_engine

from app.core.database import create_database_engine
from app.core.redis import create_redis_client

# Nothing listens on port 1, so connecting fails at once (connection refused).
CLOSED_PORT_DATABASE_URL = "postgresql+psycopg://colivo:unused@127.0.0.1:1/colivo"
CLOSED_PORT_REDIS_URL = "redis://127.0.0.1:1/0"

# A non-routable address: packets are dropped, so a connection attempt hangs
# until it times out (the slow failure a cut network gives).
BLACKHOLED_DATABASE_URL = "postgresql+psycopg://colivo:unused@10.255.255.1:5432/colivo"
BLACKHOLED_REDIS_URL = "redis://10.255.255.1:6379/0"


@pytest.fixture
def unreachable_session() -> Iterator[Session]:
    """A real session on a database address where nothing listens."""
    engine = create_engine(CLOSED_PORT_DATABASE_URL, poolclass=NullPool)
    with Session(engine) as session:
        yield session
    engine.dispose()


@pytest.fixture
def unreachable_redis() -> Iterator[Redis]:
    """A real Redis client on an address where nothing listens."""
    client = Redis.from_url(CLOSED_PORT_REDIS_URL)
    yield client
    client.close()


@pytest.fixture
def blackholed_session() -> Iterator[Session]:
    """A session built like the app's, on an address that never answers."""
    engine = create_database_engine(BLACKHOLED_DATABASE_URL)
    with Session(engine) as session:
        yield session
    engine.dispose()


@pytest.fixture
def blackholed_redis() -> Iterator[Redis]:
    """A Redis client built like the app's, on an address that never answers."""
    client = create_redis_client(BLACKHOLED_REDIS_URL)
    yield client
    client.close()
