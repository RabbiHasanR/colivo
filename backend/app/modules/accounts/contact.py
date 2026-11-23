from typing import Annotated

import phonenumbers
from email_validator import EmailNotValidError, validate_email
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
    typed = raw.strip()
    if "@" in typed:
        return Contact(channel=Channel.EMAIL, value=normalise_email(typed))
    return Contact(channel=Channel.SMS, value=normalise_phone(typed))


def normalise_email(typed: str) -> str:
    """Check an email and put it in lower case: one address, one person.

    Args:
        typed: The email as typed.

    Returns:
        The email in lower case.

    Raises:
        ValueError: When it isn't a valid email.
    """
    try:
        email = validate_email(typed, check_deliverability=False)
    except EmailNotValidError as error:
        raise ValueError(NOT_A_CONTACT) from error
    return email.normalized.lower()


def normalise_phone(typed: str) -> str:
    """Check a phone number and put it in E.164: one number, one person.

    Args:
        typed: The number as typed; without a country code it is Bangladeshi.

    Returns:
        The number in E.164, e.g. ``+8801712345678``.

    Raises:
        ValueError: When it isn't a valid phone number.
    """
    try:
        number = phonenumbers.parse(typed, DEFAULT_PHONE_REGION)
    except phonenumbers.NumberParseException as error:
        raise ValueError(NOT_A_CONTACT) from error
    if not phonenumbers.is_valid_number(number):
        raise ValueError(NOT_A_CONTACT)
    return phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)


# A request field holding a phone or an email: a string in the API contract,
# a `Contact` in the code.
ContactIn = Annotated[
    Contact,
    BeforeValidator(parse_contact),
    WithJsonSchema({"type": "string", "description": "A phone number or an email"}),
]


def partly_hidden(contact: Contact) -> str:
    """Show only enough of a phone or email for its owner to recognise it.

    Used in the notice to a person's old phone or email (Phase 1c), in case
    that phone is in the wrong hands.

    Args:
        contact: A phone (E.164) or an email.

    Returns:
        ``…678`` for a phone, ``m…@example.com`` for an email.
    """
    if contact.channel == Channel.EMAIL:
        name, domain = contact.value.split("@", 1)
        return f"{name[0]}…@{domain}"
    return f"…{contact.value[-3:]}"
