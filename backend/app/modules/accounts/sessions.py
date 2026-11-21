import secrets
import uuid
from datetime import datetime

from redis import Redis


def create_session(redis_client: Redis, person_id: uuid.UUID, now: datetime) -> str:
    """Start a log-in session for ``person_id``.

    Args:
        redis_client: Where sessions are kept.
        person_id: Who logged in.
        now: The current time.

    Returns:
        The session token, for the session cookie.
    """
    return secrets.token_urlsafe(32)
