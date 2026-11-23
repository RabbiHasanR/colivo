import uuid
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


def test_new_code_waits_a_minute_after_the_last(
    redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN a code was just sent to 01712 345678
    WHEN  another is asked for at once, and again a minute later
    THEN  at once it is refused with 429 "too_soon", 60 seconds to wait;
          a minute later it is sent
    """
    codes.issue_code(redis_client, PHONE, clock())

    with pytest.raises(HTTPException) as at_once:
        codes.issue_code(redis_client, PHONE, clock())
    clock.advance(timedelta(minutes=1))
    codes.issue_code(redis_client, PHONE, clock())

    assert code_error(at_once) == (
        429,
        CodeErrorOut(reason=CodeErrorReason.TOO_SOON, retry_in_seconds=60),
    )


def test_only_5_codes_an_hour(redis_client: Redis, clock: MovableClock) -> None:
    """
    GIVEN 5 codes were sent to 01712 345678, a minute apart (minutes 0 to 4)
    WHEN  a 6th is asked for at minute 5, and again at minute 60
    THEN  at minute 5 it is refused with 429 "hourly_limit", to wait until the
          first is an hour old (55 minutes); at minute 60 it is sent
    """
    for _ in range(5):
        codes.issue_code(redis_client, PHONE, clock())
        clock.advance(timedelta(minutes=1))

    with pytest.raises(HTTPException) as sixth:
        codes.issue_code(redis_client, PHONE, clock())
    clock.advance(timedelta(minutes=55))
    codes.issue_code(redis_client, PHONE, clock())

    assert code_error(sixth) == (
        429,
        CodeErrorOut(reason=CodeErrorReason.HOURLY_LIMIT, retry_in_seconds=55 * 60),
    )


def test_new_code_replaces_the_old_one(
    redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN a code was sent to 01712 345678, and a minute later a new one
    WHEN  the old code is typed, then the new one
    THEN  the old code is refused with 400 "expired" (not a wrong try); the
          new one works
    """
    old_code = codes.issue_code(redis_client, PHONE, clock())
    clock.advance(timedelta(minutes=1))
    new_code = codes.issue_code(redis_client, PHONE, clock())

    with pytest.raises(HTTPException) as old:
        codes.use_code(redis_client, PHONE, old_code, clock())
    codes.use_code(redis_client, PHONE, new_code, clock())

    assert code_error(old) == (400, CodeErrorOut(reason=CodeErrorReason.EXPIRED))


# Phase 1c: codes that confirm a new phone or email for one person.
CHANGE = codes.change_scope(uuid.UUID("01a1fd00-0000-7000-8000-000000000010"))


def test_a_change_code_cannot_log_in(redis_client: Redis, clock: MovableClock) -> None:
    """
    GIVEN a code was sent to 01712 345678 to confirm it as someone's new phone
    WHEN  that code is used to log in with 01712 345678
    THEN  it is refused as expired: no log-in code is waiting
    """
    code = codes.issue_code(redis_client, PHONE, clock(), scope=CHANGE)

    with pytest.raises(HTTPException) as error:
        codes.use_code(redis_client, PHONE, code, clock())

    assert code_error(error) == (400, CodeErrorOut(reason=CodeErrorReason.EXPIRED))


def test_log_in_and_change_codes_share_the_send_limit(
    redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN a log-in code was just sent to 01712 345678
    WHEN  a change code is asked for the same phone within the minute
    THEN  it is refused as too soon: one phone, one limit
    """
    codes.issue_code(redis_client, PHONE, clock())

    with pytest.raises(HTTPException) as error:
        codes.issue_code(redis_client, PHONE, clock(), scope=CHANGE)

    status, data = code_error(error)
    assert (status, getattr(data, "reason", None)) == (429, CodeErrorReason.TOO_SOON)


def test_wrong_change_codes_do_not_lock_log_in(
    redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN 5 wrong codes were typed for a change to 01712 345678 (now locked)
    WHEN  01712 345678 logs in with a log-in code a minute later
    THEN  the log-in code works: each kind of code has its own lock
    """
    change_code = codes.issue_code(redis_client, PHONE, clock(), scope=CHANGE)
    wrong = "000000" if change_code != "000000" else "111111"
    for _ in range(5):
        with pytest.raises(HTTPException):
            codes.use_code(redis_client, PHONE, wrong, clock(), scope=CHANGE)
    clock.advance(timedelta(minutes=1))

    log_in_code = codes.issue_code(redis_client, PHONE, clock())
    codes.use_code(redis_client, PHONE, log_in_code, clock())
