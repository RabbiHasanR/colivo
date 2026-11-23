import hashlib
import hmac
import json
import math
import secrets
import uuid
from datetime import UTC, datetime

from redis import Redis

from app.core.exceptions import AppError
from app.modules.accounts.constants import (
    CHANGE_CODE_PREFIX,
    CODE_LENGTH,
    CODE_LIFETIME,
    CODE_LOCK,
    CODE_MAX_PER_HOUR,
    CODE_MAX_WRONG,
    CODE_RESEND_AFTER,
    CODE_SEND_WINDOW,
)
from app.modules.accounts.contact import Contact
from app.modules.accounts.schemas import CodeErrorOut, CodeErrorReason

WRONG_CODE = "That code isn't right."
EXPIRED_CODE = "This code expired. Codes work for 5 minutes."
LOCKED = "Too many wrong codes. Try again later."
TOO_SOON = "A new code can be sent once a minute."
HOURLY_LIMIT = "Only 5 codes can be sent in an hour."


# Log-in and sign-up codes; their Redis keys are the same as before Phase 1c.
LOG_IN_SCOPE = "otp"


def change_scope(person_id: uuid.UUID) -> str:
    """The scope of codes confirming a new phone or email for ``person_id``.

    Bound to whose log-in changes, so a code for one person's change can't
    confirm another's, and none of them can log anyone in.
    """
    return f"{CHANGE_CODE_PREFIX}:{person_id}"


def code_key(contact: Contact, scope: str) -> str:
    """The Redis key of the code sent to ``contact``."""
    return f"{scope}:{contact.value}"


def wrong_key(contact: Contact, scope: str) -> str:
    """The Redis key counting wrong codes typed for ``contact``'s code."""
    return f"{scope}:wrong:{contact.value}"


def lock_key(contact: Contact, scope: str) -> str:
    """The Redis key holding when ``contact``'s lock ends."""
    return f"{scope}:lock:{contact.value}"


def seconds_until(end: datetime, now: datetime) -> int:
    """Whole seconds from ``now`` to ``end``, rounded up."""
    return math.ceil((end - now).total_seconds())


def check_not_locked(
    redis_client: Redis, contact: Contact, now: datetime, scope: str = LOG_IN_SCOPE
) -> None:
    """Refuse while ``contact`` is locked after too many wrong codes (FR-94).

    Raises:
        AppError: 429 "locked", with the seconds left.
    """
    stored = redis_client.get(lock_key(contact, scope))
    if not isinstance(stored, bytes):
        return
    until = datetime.fromisoformat(stored.decode())
    if now < until:
        raise AppError(
            429,
            LOCKED,
            CodeErrorOut(
                reason=CodeErrorReason.LOCKED,
                retry_in_seconds=seconds_until(until, now),
            ),
        )


def sent_key(contact: Contact) -> str:
    """The Redis key holding when codes were sent to ``contact``."""
    return f"otp:sent:{contact.value}"


def record_send(redis_client: Redis, contact: Contact, now: datetime) -> None:
    """Refuse a new code too soon or over the hourly limit; otherwise note it.

    Send times are a sorted set scored by time; sends older than an hour are
    dropped first, in the same transaction that reads the rest.

    Raises:
        AppError: 429 "too_soon" within a minute of the last code; 429
            "hourly_limit" when 5 were sent in the last hour. Both say how
            many seconds to wait.
    """
    key = sent_key(contact)
    window_start = (now - CODE_SEND_WINDOW).timestamp()
    with redis_client.pipeline(transaction=True) as pipe:
        pipe.zremrangebyscore(key, "-inf", window_start)
        pipe.zrange(key, 0, -1, withscores=True)
        _, sends = pipe.execute()
    times = sorted(datetime.fromtimestamp(score, UTC) for _, score in sends)
    if times and now < times[-1] + CODE_RESEND_AFTER:
        refuse_send(
            CodeErrorReason.TOO_SOON, TOO_SOON, times[-1] + CODE_RESEND_AFTER, now
        )
    if len(times) >= CODE_MAX_PER_HOUR:
        refuse_send(
            CodeErrorReason.HOURLY_LIMIT, HOURLY_LIMIT, times[0] + CODE_SEND_WINDOW, now
        )
    with redis_client.pipeline(transaction=True) as pipe:
        pipe.zadd(key, {now.isoformat(): now.timestamp()})
        pipe.expire(key, CODE_SEND_WINDOW)
        pipe.execute()


def refuse_send(
    reason: CodeErrorReason, message: str, allowed_at: datetime, now: datetime
) -> None:
    """Refuse a new code until ``allowed_at``.

    Raises:
        AppError: 429 with ``reason`` and the seconds to wait.
    """
    raise AppError(
        429,
        message,
        CodeErrorOut(reason=reason, retry_in_seconds=seconds_until(allowed_at, now)),
    )


def old_codes_key(contact: Contact, scope: str) -> str:
    """The Redis key holding the hashes of codes a newer one replaced."""
    return f"{scope}:old:{contact.value}"


def code_hash(contact: Contact, code: str) -> str:
    """Hash a code with its contact, so Redis never holds a code in plain text.

    Six digits are quick to guess, so this only keeps codes out of plain
    view; the real protection is the lock after 5 wrong codes (FR-94).
    """
    return hashlib.sha256(f"{contact.value}:{code}".encode()).hexdigest()


def issue_code(
    redis_client: Redis, contact: Contact, now: datetime, scope: str = LOG_IN_SCOPE
) -> str:
    """Make a new one-time code for ``contact``; it replaces any earlier one.

    Args:
        redis_client: Where codes are kept.
        contact: The phone or email the code is for.
        now: The current time.
        scope: What the code is for: logging in, or one person's change.

    Returns:
        The code, ``CODE_LENGTH`` digits.

    Raises:
        AppError: 429 "locked" while the contact is locked; 429 "too_soon"
            within a minute of the last code.
    """
    check_not_locked(redis_client, contact, now, scope)
    # The send limit is per phone or email whatever the scope, so nobody can
    # flood a number by mixing log-in and change codes.
    record_send(redis_client, contact, now)
    code = f"{secrets.randbelow(10**CODE_LENGTH):0{CODE_LENGTH}d}"
    stored = {
        "hash": code_hash(contact, code),
        "expires_at": (now + CODE_LIFETIME).isoformat(),
    }
    previous = redis_client.get(code_key(contact, scope))
    with redis_client.pipeline(transaction=True) as pipe:
        if isinstance(previous, bytes):
            # Replaced, not wrong: typing it later answers "expired".
            pipe.sadd(old_codes_key(contact, scope), json.loads(previous)["hash"])
            pipe.expire(old_codes_key(contact, scope), CODE_SEND_WINDOW)
        # Compared with the app's clock; the Redis expiry only clears old keys.
        pipe.set(code_key(contact, scope), json.dumps(stored), ex=CODE_LIFETIME)
        pipe.execute()
    return code


def use_code(
    redis_client: Redis,
    contact: Contact,
    code: str,
    now: datetime,
    scope: str = LOG_IN_SCOPE,
) -> None:
    """Use ``code`` for ``contact``; a code works once.

    Args:
        redis_client: Where codes are kept.
        contact: The phone or email the code was sent to.
        code: The code the person typed.
        now: The current time.
        scope: What the code must be for: logging in, or one person's change.

    Raises:
        AppError: 429 "locked" while locked; 400 "expired" when no code is
            waiting, it is 5 minutes old, or a newer code replaced it.
        AppError: 400 "wrong", with the tries left, for another code.
    """
    check_not_locked(redis_client, contact, now, scope)
    stored = redis_client.get(code_key(contact, scope))
    if not isinstance(stored, bytes):
        raise AppError(400, EXPIRED_CODE, CodeErrorOut(reason=CodeErrorReason.EXPIRED))
    sent = json.loads(stored)
    if now >= datetime.fromisoformat(sent["expires_at"]):
        raise AppError(400, EXPIRED_CODE, CodeErrorOut(reason=CodeErrorReason.EXPIRED))
    typed = code_hash(contact, code)
    if not hmac.compare_digest(sent["hash"], typed):
        if redis_client.sismember(old_codes_key(contact, scope), typed):
            raise AppError(
                400, EXPIRED_CODE, CodeErrorOut(reason=CodeErrorReason.EXPIRED)
            )
        count_wrong_code(redis_client, contact, now, scope)
    redis_client.delete(code_key(contact, scope))


def count_wrong_code(
    redis_client: Redis, contact: Contact, now: datetime, scope: str
) -> None:
    """Count a wrong code for ``contact`` and refuse it; lock it at the 5th.

    ``INCR`` is atomic, so two guesses sent at once can't both count as one.

    Raises:
        AppError: 429 "locked" at the 5th wrong code; otherwise 400 "wrong",
            with the tries left.
    """
    with redis_client.pipeline(transaction=True) as pipe:
        pipe.incr(wrong_key(contact, scope))
        pipe.expire(wrong_key(contact, scope), CODE_LIFETIME)
        wrong, _ = pipe.execute()
    if wrong >= CODE_MAX_WRONG:
        redis_client.set(
            lock_key(contact, scope), (now + CODE_LOCK).isoformat(), ex=CODE_LOCK
        )
        redis_client.delete(wrong_key(contact, scope))
        check_not_locked(redis_client, contact, now, scope)
    raise AppError(
        400,
        WRONG_CODE,
        CodeErrorOut(reason=CodeErrorReason.WRONG, tries_left=CODE_MAX_WRONG - wrong),
    )
