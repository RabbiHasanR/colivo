from datetime import date

import pytest
from sqlmodel import Session

from app.modules.accounts.models import Membership, Person, Role
from app.modules.homes import service
from app.modules.homes.models import Home
from app.modules.homes.schemas import SetupStep


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


def test_new_home_checklist_has_only_home_created_done(session: Session) -> None:
    """
    GIVEN "Our Flat", just created
    WHEN  its setup checklist is read
    THEN  it lists, in order, home created (done), then members, rooms and rent,
          home rules and bills (not done)
    """
    home = service.create_home(
        session, name="Our Flat", area=None, first_month=date(2026, 11, 1)
    )

    setup = service.get_setup(session, home.id)

    assert setup.steps == [
        SetupStep(key="home_created", done=True),
        SetupStep(key="members", done=False),
        SetupStep(key="rooms", done=False),
        SetupStep(key="rules", done=False),
        SetupStep(key="bills", done=False),
    ]


def test_members_step_is_done_once_another_member_is_active(session: Session) -> None:
    """
    GIVEN "Our Flat" with its owner and one active member, Maruf
    WHEN  its setup checklist is read
    THEN  "Add members" is done
    """

    home = service.create_home(
        session, name="Our Flat", area=None, first_month=date(2026, 11, 1)
    )
    people = [Person(phone="+8801712345678"), Person(phone="+8801812345678")]
    session.add_all(people)
    session.flush()
    session.add_all(
        [
            Membership(
                home_id=home.id, person_id=people[0].id, name="Rabbi", role=Role.OWNER
            ),
            Membership(home_id=home.id, person_id=people[1].id, name="Maruf"),
        ]
    )
    session.flush()

    setup = service.get_setup(session, home.id)

    assert SetupStep(key="members", done=True) in setup.steps
