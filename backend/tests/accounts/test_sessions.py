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
