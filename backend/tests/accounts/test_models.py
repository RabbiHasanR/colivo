from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.modules.accounts.models import Membership, Person, Role
from app.modules.homes import service as homes_service
from app.modules.homes.models import Home

LONG = "x" * 81


def our_flat(**changes: object) -> Home:
    """A valid home, with any column changed."""
    return Home.model_validate(
        {
            "code": "OF-4827",
            "name": "Our Flat",
            "area": "Mirpur",
            "first_month": date(2026, 11, 1),
        }
        | changes
    )


@pytest.mark.parametrize(
    ("home_changes", "member_name"),
    [
        pytest.param({"name": "  "}, "Rabbi Hasan", id="blank home name"),
        pytest.param({"name": LONG}, "Rabbi Hasan", id="home name over 80"),
        pytest.param({"area": LONG}, "Rabbi Hasan", id="area over 80"),
        pytest.param(
            {"first_month": date(2026, 11, 2)}, "Rabbi Hasan", id="month not on the 1st"
        ),
        pytest.param({"code": "of-48"}, "Rabbi Hasan", id="badly formed Home ID"),
        pytest.param({}, "  ", id="blank member name"),
        pytest.param({}, LONG, id="member name over 80"),
    ],
)
def test_home_and_member_checks_reject_bad_rows(
    session: Session, home_changes: dict[str, object], member_name: str
) -> None:
    """
    GIVEN a home and its owner, one of them with a bad value
    WHEN  they are saved straight to the database, past the API's checks
    THEN  the database refuses them
    """
    person = Person(phone="+8801712345678")
    home = our_flat(**home_changes)
    session.add_all([person, home])

    with pytest.raises(IntegrityError):
        session.flush()
        session.add(
            Membership(
                home_id=home.id, person_id=person.id, name=member_name, role=Role.OWNER
            )
        )
        session.flush()


def test_person_cannot_have_two_active_memberships(session: Session) -> None:
    """
    GIVEN a person who is an active member of "Our Flat"
    WHEN  an active membership of "Old Fort" is saved for them, past the service
    THEN  the database refuses it (one active home per person, FR-85)
    """
    person = Person(phone="+8801712345678")
    session.add(person)
    homes = [
        homes_service.create_home(
            session, name=name, area=None, first_month=date(2026, 11, 1)
        )
        for name in ("Our Flat", "Old Fort")
    ]
    session.add(Membership(home_id=homes[0].id, person_id=person.id, name="Rabbi"))
    session.flush()

    session.add(Membership(home_id=homes[1].id, person_id=person.id, name="Rabbi"))

    with pytest.raises(IntegrityError):
        session.flush()
