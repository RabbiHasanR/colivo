from datetime import date

import pytest
from sqlmodel import Session

from app.modules.homes import service
from app.modules.homes.models import Home


@pytest.mark.parametrize(
    ("name", "code"),
    [
        pytest.param("Our Flat", "OF-4827", id="two words"),
        pytest.param("our flat 2", "OF-4827", id="lower case, three words"),
        pytest.param("Sunrise", "SU-4827", id="one word"),
        pytest.param("A", "AX-4827", id="one letter"),
        pytest.param("বাড়ি", "XX-4827", id="no Latin letters"),
    ],
)
def test_home_code_takes_two_letters_from_the_name(name: str, code: str) -> None:
    """
    GIVEN a home name and the drawn digits 4827
    WHEN  its Home ID is made
    THEN  it is two letters from the name, a dash and the digits
    """
    assert service.home_code_for(name, "4827") == code


def test_home_code_is_drawn_again_when_taken(session: Session) -> None:
    """
    GIVEN "Our Flat" already has the Home ID OF-1111
    WHEN  another "Our Flat" is created and the first digits drawn are 1111
    THEN  new digits are drawn, and it gets OF-2222
    """
    session.add(Home(name="Our Flat", code="OF-1111", first_month=date(2026, 11, 1)))
    session.flush()
    draws = iter(["1111", "2222"])

    home = service.create_home(
        session,
        name="Our Flat",
        area=None,
        first_month=date(2026, 11, 1),
        draw_digits=lambda: next(draws),
    )

    assert home.code == "OF-2222"
