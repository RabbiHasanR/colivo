from redis import Redis, RedisError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session

from app.modules.health.schemas import HealthOut, ServiceStatus


def check_database(session: Session) -> ServiceStatus:
    """Return whether the database answers a trivial query.

    Args:
        session: A database session.

    Returns:
        ``ok`` if ``SELECT 1`` succeeds, ``down`` if the database can't be reached.
    """
    try:
        session.connection().execute(text("SELECT 1"))
    except SQLAlchemyError:
        return ServiceStatus.DOWN
    return ServiceStatus.OK


def check_redis(redis_client: Redis) -> ServiceStatus:
    """Return whether Redis answers a ping.

    Args:
        redis_client: A Redis client.

    Returns:
        ``ok`` if ``PING`` succeeds, ``down`` if Redis can't be reached.
    """
    try:
        redis_client.ping()
    except RedisError:
        return ServiceStatus.DOWN
    return ServiceStatus.OK


def get_health(session: Session, redis_client: Redis) -> HealthOut:
    """Check the database and Redis.

    Args:
        session: A database session.
        redis_client: A Redis client.

    Returns:
        The status of each dependency.
    """
    return HealthOut(
        database=check_database(session),
        redis=check_redis(redis_client),
    )


def is_healthy(health: HealthOut) -> bool:
    """Return whether every dependency is ok.

    Args:
        health: The result of ``get_health``.

    Returns:
        True when the database and Redis are both ``ok``.
    """
    return health.database is ServiceStatus.OK and health.redis is ServiceStatus.OK
