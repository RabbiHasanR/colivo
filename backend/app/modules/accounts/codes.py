import hashlib
import hmac
import json
import secrets
from datetime import datetime

from redis import Redis
from starlette.exceptions import HTTPException

from app.core.exceptions import AppError
from app.modules.accounts.constants import CODE_LENGTH, CODE_LIFETIME
from app.modules.accounts.contact import Contact
from app.modules.accounts.schemas import CodeErrorOut, CodeErrorReason

WRONG_CODE = "That code isn't right."
EXPIRED_CODE = "This code expired. Codes work for 5 minutes."


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
        AppError: 400 "expired" when no code is waiting or it is 5 minutes old.
        HTTPException: 400 when the code isn't the one sent.
    """
    stored = redis_client.get(code_key(contact))
    if not isinstance(stored, bytes):
        raise AppError(400, EXPIRED_CODE, CodeErrorOut(reason=CodeErrorReason.EXPIRED))
    sent = json.loads(stored)
    if now >= datetime.fromisoformat(sent["expires_at"]):
        raise AppError(400, EXPIRED_CODE, CodeErrorOut(reason=CodeErrorReason.EXPIRED))
    if not hmac.compare_digest(sent["hash"], code_hash(contact, code)):
        raise HTTPException(400, WRONG_CODE)
    redis_client.delete(code_key(contact))
