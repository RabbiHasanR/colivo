import uuid
from datetime import timedelta

from redis import Redis

from app.modules.accounts import sessions
from tests.conftest import MovableClock


def test_session_ends_30_days_after_its_last_use(
    redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN someone logged in on day 0
    WHEN  they come back on day 29 and day 58, then not for 31 days
    THEN  each use keeps them logged in for 30 more days; after 31 days unused
          the session is gone
    """
    person_id = uuid.uuid7()
    token = sessions.create_session(redis_client, person_id, clock())

    clock.advance(timedelta(days=29))
    on_day_29 = sessions.read_session(redis_client, token, clock())
    clock.advance(timedelta(days=29))
    on_day_58 = sessions.read_session(redis_client, token, clock())
    clock.advance(timedelta(days=31))
    after_31_days_unused = sessions.read_session(redis_client, token, clock())

    assert (on_day_29, on_day_58, after_31_days_unused) == (person_id, person_id, None)


RABBI = uuid.UUID("01a1fd00-0000-7000-8000-000000000002")


def test_ending_a_persons_sessions_ends_every_one(
    redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN Rabbi is logged in on two browsers
    WHEN  all his sessions are ended
    THEN  neither browser's session works any more
    """
    phone = sessions.create_session(redis_client, RABBI, clock())
    laptop = sessions.create_session(redis_client, RABBI, clock())

    sessions.end_sessions(redis_client, RABBI)

    assert sessions.read_session(redis_client, phone, clock()) is None
    assert sessions.read_session(redis_client, laptop, clock()) is None


def test_ending_a_persons_sessions_can_keep_one(
    redis_client: Redis, clock: MovableClock
) -> None:
    """
    GIVEN Rabbi is logged in on his phone and his laptop
    WHEN  his sessions are ended keeping the laptop's (he changed his log-in there)
    THEN  the laptop stays logged in, and the phone doesn't
    """
    phone = sessions.create_session(redis_client, RABBI, clock())
    laptop = sessions.create_session(redis_client, RABBI, clock())

    sessions.end_sessions(redis_client, RABBI, keep_token=laptop)

    assert sessions.read_session(redis_client, phone, clock()) is None
    assert sessions.read_session(redis_client, laptop, clock()) == RABBI
