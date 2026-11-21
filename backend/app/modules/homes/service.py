from datetime import date, datetime
from zoneinfo import ZoneInfo

from starlette.exceptions import HTTPException


def month_start(day: date) -> date:
    """Return the first day of ``day``'s month.

    Args:
        day: Any date.

    Returns:
        The 1st of that month.
    """
    return day.replace(day=1)


def next_month_start(day: date) -> date:
    """Return the first day of the month after ``day``'s.

    Args:
        day: Any date.

    Returns:
        The 1st of the next month.
    """
    if day.month == 12:
        return date(day.year + 1, 1, 1)
    return date(day.year, day.month + 1, 1)


def check_first_month(first_month: date, now: datetime, time_zone: str) -> None:
    """Allow only this month or next as a new home's first month (FR-83).

    "This month" is the month in the home's time zone, not the server's.

    Args:
        first_month: The chosen first month, as its 1st.
        now: The current time.
        time_zone: The home's time zone, e.g. ``Asia/Dhaka``.

    Raises:
        HTTPException: 400 when it is another month or not on the 1st.
    """
    today = now.astimezone(ZoneInfo(time_zone)).date()
    if first_month not in {month_start(today), next_month_start(today)}:
        raise HTTPException(400, "The first month must be this month or next.")
