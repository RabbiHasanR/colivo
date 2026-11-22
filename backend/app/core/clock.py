from collections.abc import Callable
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends

# Returns the current time, timezone-aware.
type Clock = Callable[[], datetime]


def utc_now() -> datetime:
    """Return the current time in UTC.

    Returns:
        A timezone-aware ``datetime``.
    """
    return datetime.now(UTC)


def get_clock() -> Clock:
    """Return the app's clock (a FastAPI dependency, overridden in tests to move time).

    Returns:
        A function giving the current time.
    """
    return utc_now


# The clock for an endpoint or service call: `clock: ClockDep`, then `clock()`.
ClockDep = Annotated[Clock, Depends(get_clock)]
