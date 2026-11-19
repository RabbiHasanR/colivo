from collections.abc import Iterator

import pytest
from redis import Redis
from sqlalchemy import NullPool
from sqlmodel import Session, create_engine

from app.core.redis import redis_client
from app.modules.health.schemas import HealthOut, ServiceStatus
from app.modules.health.service import get_health

# Nothing listens on port 1, so connecting fails at once (connection refused).
CLOSED_PORT_DATABASE_URL = "postgresql+psycopg://colivo:unused@127.0.0.1:1/colivo"
CLOSED_PORT_REDIS_URL = "redis://127.0.0.1:1/0"


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


@pytest.mark.parametrize(
    ("down", "expected"),
    [
        pytest.param(
            "database",
            HealthOut(database=ServiceStatus.DOWN, redis=ServiceStatus.OK),
            id="database",
        ),
        pytest.param(
            "redis",
            HealthOut(database=ServiceStatus.OK, redis=ServiceStatus.DOWN),
            id="redis",
        ),
    ],
)
def test_health_reports_the_dependency_that_is_down(
    down: str,
    expected: HealthOut,
    session: Session,
    unreachable_session: Session,
    unreachable_redis: Redis,
) -> None:
    """
    GIVEN one dependency can't be reached and the other is running
    WHEN  the health is checked
    THEN  the unreachable one is "down" and the other "ok"
    """
    db_session = unreachable_session if down == "database" else session
    client = unreachable_redis if down == "redis" else redis_client

    assert get_health(db_session, client) == expected
