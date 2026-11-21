import pytest
from redis import Redis
from starlette.exceptions import HTTPException

from app.core.notifier import Channel
from app.modules.accounts import codes
from app.modules.accounts.contact import Contact
from tests.conftest import MovableClock

PHONE = Contact(channel=Channel.SMS, value="+8801712345678")


def test_code_works_only_once(redis_client: Redis, clock: MovableClock) -> None:
    """
    GIVEN a code that was just used to log in or sign up
    WHEN  it is used again
    THEN  it is refused with 400
    """
    code = codes.issue_code(redis_client, PHONE, clock())
    codes.use_code(redis_client, PHONE, code, clock())

    with pytest.raises(HTTPException) as error:
        codes.use_code(redis_client, PHONE, code, clock())

    assert error.value.status_code == 400
