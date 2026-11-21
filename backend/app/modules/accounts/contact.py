from typing import Annotated

from pydantic import BaseModel, BeforeValidator, WithJsonSchema

from app.core.notifier import Channel


class Contact(BaseModel, frozen=True):
    """A phone (E.164) or an email address (lower case), and how to reach it."""

    channel: Channel
    value: str


def parse_contact(raw: object) -> object:
    """Read a typed phone or email into a ``Contact``.

    Args:
        raw: What the person typed, or an already parsed ``Contact``.

    Returns:
        The ``Contact`` for a string; anything else unchanged, for Pydantic.
    """
    if isinstance(raw, str):
        return Contact(channel=Channel.SMS, value=raw)
    return raw


# A request field holding a phone or an email: a string in the API contract,
# a `Contact` in the code.
ContactIn = Annotated[
    Contact,
    BeforeValidator(parse_contact),
    WithJsonSchema({"type": "string", "description": "A phone number or an email"}),
]
