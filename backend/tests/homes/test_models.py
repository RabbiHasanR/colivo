from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.modules.homes.models import Home


def test_two_homes_cannot_share_a_code(session: Session) -> None:
    """
    GIVEN a home with the Home ID OF-4827
    WHEN  another home is saved with the same ID, past the service's check
    THEN  the database refuses it
    """
    session.add(Home(code="OF-4827", name="Our Flat", first_month=date(2026, 11, 1)))
    session.flush()

    session.add(Home(code="OF-4827", name="Old Fort", first_month=date(2026, 11, 1)))

    with pytest.raises(IntegrityError):
        session.flush()
