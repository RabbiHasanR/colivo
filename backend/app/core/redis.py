from typing import Annotated

from fastapi import Depends
from redis import Redis

from app.core.config import settings


def create_redis_client(url: str) -> Redis:
    """Create the Redis client the app uses for ``url``.

    Args:
        url: A Redis URL.

    Returns:
        The client.
    """
    return Redis.from_url(
        url,
        socket_connect_timeout=settings.connect_timeout_seconds,
        socket_timeout=settings.connect_timeout_seconds,
    )


redis_client = create_redis_client(settings.redis_url)


def get_redis() -> Redis:
    """Return the shared Redis client (a FastAPI dependency, overridable in tests).

    Returns:
        The application's Redis client.
    """
    return redis_client


# The Redis client for an endpoint: `redis_client: RedisDep`.
RedisDep = Annotated[Redis, Depends(get_redis)]
