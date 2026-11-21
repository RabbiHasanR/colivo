import hashlib
import hmac
import json
import math
import secrets
from datetime import datetime

from redis import Redis

from app.core.exceptions import AppError
from app.modules.accounts.constants import (
    CODE_LENGTH,
    CODE_LIFETIME,
    CODE_LOCK,
    CODE_MAX_WRONG,
)
from app.modules.accounts.contact import Contact
from app.modules.accounts.schemas import CodeErrorOut, CodeErrorReason

WRONG_CODE = "That code isn't right."
EXPIRED_CODE = "This code expired. Codes work for 5 minutes."
LOCKED = "Too many wrong codes. Try again later."


def code_key(contact: Contact) -> str:
    """The Redis key of the code sent to ``contact``."""
    return f"otp:{contact.value}"


def wrong_key(contact: Contact) -> str:
    """The Redis key counting wrong codes typed for ``contact``'s code."""
    return f"otp:wrong:{contact.value}"


def lock_key(contact: Contact) -> str:
    """The Redis key holding when ``contact``'s lock ends."""
    return f"otp:lock:{contact.value}"


def seconds_until(end: datetime, now: datetime) -> int:
    """Whole seconds from ``now`` to ``end``, rounded up."""
    return math.ceil((end - now).total_seconds())


def check_not_locked(redis_client: Redis, contact: Contact, now: datetime) -> None:
    """Refuse while ``contact`` is locked after too many wrong codes (FR-94).

    Raises:
        AppError: 429 "locked", with the seconds left.
    """
    stored = redis_client.get(lock_key(contact))
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


def code_hash(contact: Contact, code: str) -> str:
    """Hash a code with its contact, so Redis never holds a code in plain text.

    Six digits are quick to guess, so this only keeps codes out of plain
    view; the real protection is the lock after 5 wrong codes (FR-94).
    """
    return hashlib.sha256(f"{contact.value}:{code}".encode()).hexdigest()


def issue_code(redis_client: Redis, contact: Contact, now: datetime) -> str:
    """Make a new one-time code for ``contact``; it replaces any earlier one.

    Args:
        redis_client: Where codes are kept.
        contact: The phone or email the code is for.
        now: The current time.

    Returns:
        The code, ``CODE_LENGTH`` digits.

    Raises:
        AppError: 429 "locked" while the contact is locked.
    """
    check_not_locked(redis_client, contact, now)
    code = f"{secrets.randbelow(10**CODE_LENGTH):0{CODE_LENGTH}d}"
    stored = {
        "hash": code_hash(contact, code),
        "expires_at": (now + CODE_LIFETIME).isoformat(),
    }
    # Compared with the app's clock; the Redis expiry only clears old keys.
    redis_client.set(code_key(contact), json.dumps(stored), ex=CODE_LIFETIME)
    return code


def use_code(redis_client: Redis, contact: Contact, code: str, now: datetime) -> None:
    """Use ``code`` for ``contact``; a code works once.

    Args:
        redis_client: Where codes are kept.
        contact: The phone or email the code was sent to.
        code: The code the person typed.
        now: The current time.

    Raises:
        AppError: 429 "locked" while locked; 400 "expired" when no code is
            waiting or it is 5 minutes old.
        AppError: 400 "wrong", with the tries left, for another code.
    """
    check_not_locked(redis_client, contact, now)
    stored = redis_client.get(code_key(contact))
    if not isinstance(stored, bytes):
        raise AppError(400, EXPIRED_CODE, CodeErrorOut(reason=CodeErrorReason.EXPIRED))
    sent = json.loads(stored)
    if now >= datetime.fromisoformat(sent["expires_at"]):
        raise AppError(400, EXPIRED_CODE, CodeErrorOut(reason=CodeErrorReason.EXPIRED))
    if not hmac.compare_digest(sent["hash"], code_hash(contact, code)):
        count_wrong_code(redis_client, contact, now)
    redis_client.delete(code_key(contact))


def count_wrong_code(redis_client: Redis, contact: Contact, now: datetime) -> None:
    """Count a wrong code for ``contact`` and refuse it; lock it at the 5th.

    ``INCR`` is atomic, so two guesses sent at once can't both count as one.

    Raises:
        AppError: 429 "locked" at the 5th wrong code; otherwise 400 "wrong",
            with the tries left.
    """
    with redis_client.pipeline(transaction=True) as pipe:
        pipe.incr(wrong_key(contact))
        pipe.expire(wrong_key(contact), CODE_LIFETIME)
        wrong, _ = pipe.execute()
    if wrong >= CODE_MAX_WRONG:
        redis_client.set(lock_key(contact), (now + CODE_LOCK).isoformat(), ex=CODE_LOCK)
        redis_client.delete(wrong_key(contact))
        check_not_locked(redis_client, contact, now)
    raise AppError(
        400,
        WRONG_CODE,
        CodeErrorOut(reason=CodeErrorReason.WRONG, tries_left=CODE_MAX_WRONG - wrong),
    )
