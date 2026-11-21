import hashlib
import hmac
import secrets
from datetime import datetime

from redis import Redis
from starlette.exceptions import HTTPException

from app.modules.accounts.constants import CODE_LENGTH, CODE_LIFETIME
from app.modules.accounts.contact import Contact

WRONG_CODE = "That code isn't right."


def code_key(contact: Contact) -> str:
    """The Redis key of the code sent to ``contact``."""
    return f"otp:{contact.value}"


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
    """
    code = f"{secrets.randbelow(10**CODE_LENGTH):0{CODE_LENGTH}d}"
    redis_client.set(code_key(contact), code_hash(contact, code), ex=CODE_LIFETIME)
    return code


def use_code(redis_client: Redis, contact: Contact, code: str, now: datetime) -> None:
    """Use ``code`` for ``contact``; a code works once.

    Args:
        redis_client: Where codes are kept.
        contact: The phone or email the code was sent to.
        code: The code the person typed.
        now: The current time.

    Raises:
        HTTPException: 400 when there is no code, or it isn't this one.
    """
    stored = redis_client.get(code_key(contact))
    typed = code_hash(contact, code).encode()
    if not isinstance(stored, bytes) or not hmac.compare_digest(stored, typed):
        raise HTTPException(400, WRONG_CODE)
    redis_client.delete(code_key(contact))
