import re
import secrets
import uuid
from collections.abc import Callable
from datetime import date, datetime
from zoneinfo import ZoneInfo

from sqlmodel import Session, select
from starlette.exceptions import HTTPException

from app.modules.homes.constants import SETUP_STEPS
from app.modules.homes.models import Home
from app.modules.homes.schemas import SetupOut, SetupStep


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


def home_code_for(name: str, digits: str) -> str:
    """Make a Home ID such as ``OF-4827`` from a home's name (FR-88).

    The letters are the first letters of the name's first two words ("Our
    Flat" → ``OF``), or the first two of a one-word name ("Sunrise" → ``SU``).
    Only Latin letters count; missing letters are ``X``.

    Args:
        name: The home's name.
        digits: Four drawn digits.

    Returns:
        The Home ID.
    """
    words = re.findall(r"[A-Za-z]+", name)
    letters = (
        "".join(word[0] for word in words[:2]) if len(words) > 1 else "".join(words)
    )
    return f"{letters[:2].upper():X<2}-{digits}"


def random_digits() -> str:
    """Draw four random digits for a Home ID.

    Returns:
        Four digits, e.g. ``"0482"``.
    """
    return f"{secrets.randbelow(10_000):04d}"


def create_home(
    session: Session,
    *,
    name: str,
    area: str | None,
    first_month: date,
    draw_digits: Callable[[], str] = random_digits,
) -> Home:
    """Add a new home with a Home ID no other home has (not committed).

    A taken ID is drawn again. Two sign-ups drawing the same free ID at the
    same moment are stopped by the unique index (a 500, very unlikely with
    10,000 IDs per pair of letters).

    Args:
        session: The database session.
        name: The home's name.
        area: Its optional area.
        first_month: Its first month, as the 1st.
        draw_digits: Where the Home ID's digits come from (tests fix them).

    Returns:
        The home, flushed.
    """
    code = home_code_for(name, draw_digits())
    while session.exec(select(Home.id).where(Home.code == code)).first():
        code = home_code_for(name, draw_digits())
    home = Home(
        code=code,
        name=name,
        area=area,
        first_month=first_month,
    )
    session.add(home)
    session.flush()
    return home


def get_setup(session: Session, home_id: uuid.UUID) -> SetupOut:
    """The new-home checklist of ``home_id`` (FR-95).

    The home exists, so "home created" is done. Members, rooms and rent, home
    rules and bills can't be set up yet: their screens come in groups 4 and
    Phase 2, which mark them done.

    Args:
        session: The database session.
        home_id: The home.

    Returns:
        The steps in order, each done or not.
    """
    done = {"home_created"}
    return SetupOut(steps=[SetupStep(key=key, done=key in done) for key in SETUP_STEPS])
