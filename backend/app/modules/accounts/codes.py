import secrets
from datetime import datetime

from redis import Redis

from app.modules.accounts.constants import CODE_LENGTH
from app.modules.accounts.contact import Contact


def issue_code(redis_client: Redis, contact: Contact, now: datetime) -> str:
    """Make a new one-time code for ``contact``.

    Args:
        redis_client: Where codes are kept.
        contact: The phone or email the code is for.
        now: The current time.

    Returns:
        The code, ``CODE_LENGTH`` digits.
    """
    return f"{secrets.randbelow(10**CODE_LENGTH):0{CODE_LENGTH}d}"


def use_code(redis_client: Redis, contact: Contact, code: str, now: datetime) -> None:
    """Use ``code`` for ``contact``.

    Args:
        redis_client: Where codes are kept.
        contact: The phone or email the code was sent to.
        code: The code the person typed.
        now: The current time.
    """
