import time

import pytest
from redis import Redis
from sqlmodel import Session

from app.core.redis import redis_client
from app.modules.health.schemas import HealthOut, ServiceStatus
from app.modules.health.service import get_health


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


# B3: "answers within a few seconds". The timeout is 2 s; 5 s leaves headroom.
TIME_LIMIT_SECONDS = 5


@pytest.mark.parametrize(
    "down", [pytest.param("database", id="database"), pytest.param("redis", id="redis")]
)
def test_health_check_gives_up_after_the_timeout(
    down: str,
    session: Session,
    blackholed_session: Session,
    blackholed_redis: Redis,
) -> None:
    """
    GIVEN one dependency is on an address that never answers
    WHEN  the health is checked
    THEN  that dependency is "down", and the check took under 5 seconds
    """
    db_session = blackholed_session if down == "database" else session
    client = blackholed_redis if down == "redis" else redis_client

    started = time.monotonic()
    health = get_health(db_session, client)
    elapsed = time.monotonic() - started

    assert getattr(health, down) is ServiceStatus.DOWN
    assert elapsed < TIME_LIMIT_SECONDS
