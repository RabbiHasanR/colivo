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
