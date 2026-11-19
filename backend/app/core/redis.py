from typing import Annotated

from fastapi import Depends
from redis import Redis

from app.core.config import settings

redis_client = Redis.from_url(settings.redis_url)


def get_redis() -> Redis:
    """Return the shared Redis client (a FastAPI dependency, overridable in tests).

    Returns:
        The application's Redis client.
    """
    return redis_client


# The Redis client for an endpoint: `redis_client: RedisDep`.
RedisDep = Annotated[Redis, Depends(get_redis)]
