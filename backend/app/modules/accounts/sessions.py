import hashlib
import secrets
import uuid
from datetime import datetime

from redis import Redis

from app.modules.accounts.constants import SESSION_LIFETIME


def session_key(token: str) -> str:
    """The Redis key of a session: the token's hash, never the token itself."""
    return f"session:{hashlib.sha256(token.encode()).hexdigest()}"


def create_session(redis_client: Redis, person_id: uuid.UUID, now: datetime) -> str:
    """Start a log-in session for ``person_id``.

    Args:
        redis_client: Where sessions are kept.
        person_id: Who logged in.
        now: The current time.

    Returns:
        The session token, for the session cookie.
    """
    token = secrets.token_urlsafe(32)
    redis_client.set(session_key(token), str(person_id), ex=SESSION_LIFETIME)
    return token


def read_session(redis_client: Redis, token: str, now: datetime) -> uuid.UUID | None:
    """Return who a session token belongs to, if it is a live session.

    Args:
        redis_client: Where sessions are kept.
        token: The token from the session cookie.
        now: The current time.

    Returns:
        The person's id, or None for no such session.
    """
    stored = redis_client.get(session_key(token))
    if not isinstance(stored, bytes):
        return None
    return uuid.UUID(stored.decode())
