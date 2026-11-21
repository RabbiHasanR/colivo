from contextlib import AbstractContextManager, nullcontext
from datetime import timedelta

import pytest
from redis import Redis
from starlette.exceptions import HTTPException

from app.core.notifier import Channel
from app.modules.accounts import codes
from app.modules.accounts.contact import Contact
from app.modules.accounts.schemas import CodeErrorOut, CodeErrorReason
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


def code_error(error: pytest.ExceptionInfo[HTTPException]) -> tuple[int, object]:
    """The status and the ``data`` a refused code answers with."""
    return error.value.status_code, getattr(error.value, "data", None)


@pytest.mark.parametrize(
    ("after", "outcome"),
    [
        pytest.param(timedelta(minutes=4, seconds=59), nullcontext(), id="4:59"),
        pytest.param(timedelta(minutes=5), pytest.raises(HTTPException), id="5:00"),
    ],
)
def test_code_expires_after_5_minutes(
    redis_client: Redis,
    clock: MovableClock,
    after: timedelta,
    outcome: AbstractContextManager[pytest.ExceptionInfo[HTTPException] | None],
) -> None:
    """
    GIVEN a code sent to 01712 345678
    WHEN  it is used 4:59 or 5:00 later
    THEN  at 4:59 it works; at 5:00 it is refused with 400 "expired"
    """
    code = codes.issue_code(redis_client, PHONE, clock())
    clock.advance(after)

    with outcome as error:
        codes.use_code(redis_client, PHONE, code, clock())

    if error is not None:
        assert code_error(error) == (400, CodeErrorOut(reason=CodeErrorReason.EXPIRED))


def test_code_nobody_asked_for_answers_expired(
    redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN no code was sent to 01712 345678
    WHEN  someone types a code for it
    THEN  it is refused with 400 "expired": the next step is a new code
    """
    with pytest.raises(HTTPException) as error:
        codes.use_code(redis_client, PHONE, "123456", clock())

    assert code_error(error) == (400, CodeErrorOut(reason=CodeErrorReason.EXPIRED))
