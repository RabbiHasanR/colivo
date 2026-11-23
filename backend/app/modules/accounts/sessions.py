import hashlib
import json
import secrets
import uuid
from datetime import datetime

from redis import Redis

from app.modules.accounts.constants import PERSON_SESSIONS_PREFIX, SESSION_LIFETIME


def session_key(token: str) -> str:
    """The Redis key of a session: the token's hash, never the token itself."""
    return f"session:{hashlib.sha256(token.encode()).hexdigest()}"


def person_sessions_key(person_id: uuid.UUID) -> str:
    """The Redis key of the set of ``person_id``'s session keys (Phase 1c)."""
    return f"{PERSON_SESSIONS_PREFIX}:{person_id}"


def save_session(
    redis_client: Redis, token: str, person_id: uuid.UUID, now: datetime
) -> None:
    """Keep a session alive until ``SESSION_LIFETIME`` after ``now``.

    The end time is compared with the app's clock; the Redis expiry only
    clears old keys away. The session is also listed under its person, so a
    change to their log-in can end all their sessions.
    """
    value = {
        "person_id": str(person_id),
        "expires_at": (now + SESSION_LIFETIME).isoformat(),
    }
    listed = person_sessions_key(person_id)
    with redis_client.pipeline(transaction=True) as pipe:
        pipe.set(session_key(token), json.dumps(value), ex=SESSION_LIFETIME)
        pipe.sadd(listed, session_key(token))
        pipe.expire(listed, SESSION_LIFETIME)
        pipe.execute()


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
    save_session(redis_client, token, person_id, now)
    return token


def read_session(redis_client: Redis, token: str, now: datetime) -> uuid.UUID | None:
    """Return who a live session belongs to, and keep it alive 30 more days.

    Args:
        redis_client: Where sessions are kept.
        token: The token from the session cookie.
        now: The current time.

    Returns:
        The person's id, or None when there is no such session or it ended.
    """
    stored = redis_client.get(session_key(token))
    if not isinstance(stored, bytes):
        return None
    value = json.loads(stored)
    if now >= datetime.fromisoformat(value["expires_at"]):
        redis_client.delete(session_key(token))
        return None
    person_id = uuid.UUID(value["person_id"])
    save_session(redis_client, token, person_id, now)
    return person_id


def end_session(redis_client: Redis, token: str) -> None:
    """End a session at once (log-out).

    Args:
        redis_client: Where sessions are kept.
        token: The token from the session cookie.
    """
    redis_client.delete(session_key(token))


def end_sessions(
    redis_client: Redis, person_id: uuid.UUID, keep_token: str | None = None
) -> None:
    """End the sessions of ``person_id``, all but ``keep_token``'s if given.

    Used when their log-in changes: the browser that made the change can stay
    logged in, every other one logs in again.

    Args:
        redis_client: Where sessions are kept.
        person_id: Whose sessions end.
        keep_token: The token of a session to keep, if any; one that isn't
            theirs keeps nothing.
    """
    listed = person_sessions_key(person_id)
    kept = session_key(keep_token).encode() if keep_token else None
    ended = [key for key in redis_client.smembers(listed) if key != kept]
    with redis_client.pipeline(transaction=True) as pipe:
        if ended:
            pipe.delete(*ended)
            pipe.srem(listed, *ended)
        pipe.execute()
