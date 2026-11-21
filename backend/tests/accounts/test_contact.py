import pytest

from app.core.notifier import Channel
from app.modules.accounts.contact import Contact, parse_contact


@pytest.mark.parametrize(
    ("typed", "contact"),
    [
        pytest.param(
            "01712 345678",
            Contact(channel=Channel.SMS, value="+8801712345678"),
            id="local",
        ),
        pytest.param(
            "+880 1712-345678",
            Contact(channel=Channel.SMS, value="+8801712345678"),
            id="international",
        ),
        pytest.param(
            " Rabbi@Example.COM ",
            Contact(channel=Channel.EMAIL, value="rabbi@example.com"),
            id="email",
        ),
    ],
)
def test_contact_is_normalised(typed: str, contact: Contact) -> None:
    """
    GIVEN a phone typed in local or international form, or an email in any case
    WHEN  it is read as a contact
    THEN  the phone is in E.164 and the email in lower case, so each is one person
    """
    assert parse_contact(typed) == contact


@pytest.mark.parametrize("typed", ["hello", "123", "a@", "rabbi@", "@example.com", ""])
def test_contact_that_is_not_a_phone_or_email_is_rejected(typed: str) -> None:
    """
    GIVEN text that is neither a phone number nor an email
    WHEN  it is read as a contact
    THEN  it is rejected
    """
    with pytest.raises(ValueError, match="Enter a phone number or an email"):
        parse_contact(typed)
