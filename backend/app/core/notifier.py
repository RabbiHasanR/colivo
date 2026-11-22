import json
import logging
from enum import StrEnum
from typing import Annotated, Protocol

from fastapi import Depends
from redis import Redis

from app.core.redis import get_redis

logger = logging.getLogger(__name__)

# The Redis list the development notifier keeps its messages in; the
# end-to-end test reads one-time codes from it.
DEV_OUTBOX_KEY = "dev:outbox"
DEV_OUTBOX_SIZE = 100


class Channel(StrEnum):
    """How a message reaches a person."""

    SMS = "sms"
    EMAIL = "email"


class Notifier(Protocol):
    """Sends a short message to a phone (SMS) or an email address."""

    def send(self, channel: Channel, to: str, text: str) -> None:
        """Send ``text`` to ``to`` over ``channel``."""
        ...


class LogNotifier:
    """Development notifier: logs each message and keeps it in ``dev:outbox``.

    Nothing leaves the machine. Used until an SMS and email provider is chosen
    (specs/tech-stack.md → Deferred decisions).
    """

    def __init__(self, redis_client: Redis) -> None:
        self.redis_client = redis_client

    def send(self, channel: Channel, to: str, text: str) -> None:
        """Log the message and push it onto the development outbox.

        Args:
            channel: SMS or email.
            to: The phone (E.164) or email address.
            text: The message.
        """
        logger.info("%s to %s: %s", channel, to, text)
        message = json.dumps({"channel": channel, "to": to, "text": text})
        self.redis_client.lpush(DEV_OUTBOX_KEY, message)
        self.redis_client.ltrim(DEV_OUTBOX_KEY, 0, DEV_OUTBOX_SIZE - 1)


def get_notifier(redis_client: Annotated[Redis, Depends(get_redis)]) -> Notifier:
    """Return the configured notifier (a FastAPI dependency, replaced in tests).

    Args:
        redis_client: The app's Redis client.

    Returns:
        The notifier for ``settings.notifier`` (only ``log`` exists).
    """
    return LogNotifier(redis_client)


# The notifier for an endpoint: `notifier: NotifierDep`.
NotifierDep = Annotated[Notifier, Depends(get_notifier)]
