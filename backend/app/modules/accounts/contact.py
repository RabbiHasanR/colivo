from typing import Annotated

import phonenumbers
from pydantic import BaseModel, BeforeValidator, WithJsonSchema

from app.core.notifier import Channel

# Phones without a country code are read as Bangladeshi numbers.
DEFAULT_PHONE_REGION = "BD"
NOT_A_CONTACT = "Enter a phone number or an email."


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

    Raises:
        ValueError: When the text is neither a phone number nor an email.
    """
    if not isinstance(raw, str):
        return raw
    if "@" in raw:
        return Contact(channel=Channel.EMAIL, value=raw)
    try:
        number = phonenumbers.parse(raw, DEFAULT_PHONE_REGION)
    except phonenumbers.NumberParseException as error:
        raise ValueError(NOT_A_CONTACT) from error
    if not phonenumbers.is_valid_number(number):
        raise ValueError(NOT_A_CONTACT)
    return Contact(channel=Channel.SMS, value=raw)


# A request field holding a phone or an email: a string in the API contract,
# a `Contact` in the code.
ContactIn = Annotated[
    Contact,
    BeforeValidator(parse_contact),
    WithJsonSchema({"type": "string", "description": "A phone number or an email"}),
]
