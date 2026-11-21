from contextlib import AbstractContextManager, nullcontext
from datetime import datetime, timedelta

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


def wrong_code_for(code: str) -> str:
    """Another six-digit code than ``code``."""
    return f"{(int(code) + 1) % 1_000_000:06d}"


def test_wrong_code_says_how_many_tries_are_left(
    redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN a code sent to 01712 345678
    WHEN  a different code is typed
    THEN  it is refused with 400 "wrong", and 4 tries are left
    """
    code = codes.issue_code(redis_client, PHONE, clock())

    with pytest.raises(HTTPException) as error:
        codes.use_code(redis_client, PHONE, wrong_code_for(code), clock())

    assert code_error(error) == (
        400,
        CodeErrorOut(reason=CodeErrorReason.WRONG, tries_left=4),
    )


def type_wrong_codes(redis_client: Redis, code: str, now: datetime, times: int) -> None:
    """Type a wrong code ``times`` times, ignoring each refusal."""
    for _ in range(times):
        with pytest.raises(HTTPException):
            codes.use_code(redis_client, PHONE, wrong_code_for(code), now)


def test_fifth_wrong_code_locks_the_contact_for_15_minutes(
    redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN a code sent to 01712 345678, and 4 wrong codes typed
    WHEN  a 5th wrong code is typed, and then the right one
    THEN  the 5th is refused with 429 "locked", 15 minutes to wait, and so is
          the right code
    """
    code = codes.issue_code(redis_client, PHONE, clock())
    type_wrong_codes(redis_client, code, clock(), times=4)

    with pytest.raises(HTTPException) as fifth:
        codes.use_code(redis_client, PHONE, wrong_code_for(code), clock())
    with pytest.raises(HTTPException) as right_code:
        codes.use_code(redis_client, PHONE, code, clock())

    locked = (429, CodeErrorOut(reason=CodeErrorReason.LOCKED, retry_in_seconds=900))
    assert code_error(fifth) == locked
    assert code_error(right_code) == locked


def lock(redis_client: Redis, now: datetime) -> None:
    """Lock 01712 345678: a code, then 5 wrong codes."""
    code = codes.issue_code(redis_client, PHONE, now)
    type_wrong_codes(redis_client, code, now, times=5)


def test_locked_contact_cannot_get_a_new_code(
    redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN 01712 345678 is locked after 5 wrong codes
    WHEN  a new code is asked for straight away
    THEN  it is refused with 429 "locked", 15 minutes to wait
    """
    lock(redis_client, clock())

    with pytest.raises(HTTPException) as error:
        codes.issue_code(redis_client, PHONE, clock())

    assert code_error(error) == (
        429,
        CodeErrorOut(reason=CodeErrorReason.LOCKED, retry_in_seconds=900),
    )


def test_lock_ends_after_15_minutes(redis_client: Redis, clock: MovableClock) -> None:
    """
    GIVEN 01712 345678 was locked after 5 wrong codes
    WHEN  15 minutes later a new code is asked for and used
    THEN  it is sent and it works
    """
    lock(redis_client, clock())
    clock.advance(timedelta(minutes=15))

    code = codes.issue_code(redis_client, PHONE, clock())
    codes.use_code(redis_client, PHONE, code, clock())
