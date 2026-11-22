from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, func, select

from app.modules.accounts.models import (
    Membership,
    MembershipPeriod,
    MembershipStatus,
    Person,
    Role,
)
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


@pytest.mark.parametrize(
    "contact",
    [
        pytest.param({"phone": "+8801712345678"}, id="phone"),
        pytest.param({"email": "rabbi@example.com"}, id="email"),
    ],
)
def test_two_people_cannot_share_a_phone_or_email(
    session: Session, contact: dict[str, str]
) -> None:
    """
    GIVEN a person with a phone or email
    WHEN  a second person with the same one is saved, past the service
    THEN  the database refuses it: one phone or email is one person
    """
    session.add(Person.model_validate(contact))
    session.flush()

    session.add(Person.model_validate(contact))

    with pytest.raises(IntegrityError):
        session.flush()


@pytest.mark.parametrize(
    "person",
    [
        pytest.param({}, id="no phone and no email"),
        pytest.param({"phone": "01712 345678"}, id="phone not in E.164"),
        pytest.param({"email": "Rabbi@example.com"}, id="email not in lower case"),
    ],
)
def test_person_checks_reject_bad_rows(
    session: Session, person: dict[str, str]
) -> None:
    """
    GIVEN a person with no contact, a phone not in E.164 or an upper-case email
    WHEN  it is saved straight to the database
    THEN  the database refuses it
    """
    session.add(Person.model_validate(person))

    with pytest.raises(IntegrityError):
        session.flush()


def test_person_has_one_membership_per_home(session: Session) -> None:
    """
    GIVEN Maruf was a member of "Our Flat" and is now deactivated
    WHEN  a second membership of Our Flat is saved for him, past the service
    THEN  the database refuses it: he is reactivated, never added twice
    """
    person = Person(phone="+8801812345678")
    session.add(person)
    home = homes_service.create_home(
        session, name="Our Flat", area=None, first_month=date(2026, 11, 1)
    )
    session.add(
        Membership(
            home_id=home.id,
            person_id=person.id,
            name="Maruf",
            status=MembershipStatus.INACTIVE,
        )
    )
    session.flush()

    session.add(Membership(home_id=home.id, person_id=person.id, name="Maruf"))

    with pytest.raises(IntegrityError):
        session.flush()


def test_database_refuses_two_active_members_with_one_name(session: Session) -> None:
    """
    GIVEN Maruf is an active member of "Our Flat"
    WHEN  another active member named "maruf" is saved, past the service
    THEN  the database refuses it (names unique among active members, any case)
    """
    home = homes_service.create_home(
        session, name="Our Flat", area=None, first_month=date(2026, 11, 1)
    )
    people = [Person(phone="+8801812345678"), Person(phone="+8801912345678")]
    session.add_all(people)
    session.flush()
    session.add(Membership(home_id=home.id, person_id=people[0].id, name="Maruf"))
    session.flush()

    session.add(Membership(home_id=home.id, person_id=people[1].id, name="maruf"))

    with pytest.raises(IntegrityError):
        session.flush()


def test_home_has_at_most_one_owner(session: Session) -> None:
    """
    GIVEN Rabbi Hasan owns "Our Flat"
    WHEN  a second owner of Our Flat is saved, past the service
    THEN  the database refuses it: a home has exactly one owner (FR-63)
    """
    home = homes_service.create_home(
        session, name="Our Flat", area=None, first_month=date(2026, 11, 1)
    )
    people = [Person(phone="+8801712345678"), Person(phone="+8801812345678")]
    session.add_all(people)
    session.flush()
    session.add(
        Membership(
            home_id=home.id, person_id=people[0].id, name="Rabbi", role=Role.OWNER
        )
    )
    session.flush()

    session.add(
        Membership(
            home_id=home.id, person_id=people[1].id, name="Maruf", role=Role.OWNER
        )
    )

    with pytest.raises(IntegrityError):
        session.flush()


def test_stay_cannot_end_before_it_starts(session: Session) -> None:
    """
    GIVEN a member of "Our Flat"
    WHEN  a stay ending before it starts is saved, past the service
    THEN  the database refuses it
    """
    home = homes_service.create_home(
        session, name="Our Flat", area=None, first_month=date(2026, 11, 1)
    )
    person = Person(phone="+8801812345678")
    session.add(person)
    session.flush()
    member = Membership(home_id=home.id, person_id=person.id, name="Maruf")
    session.add(member)
    session.flush()

    session.add(
        MembershipPeriod(
            home_id=home.id,
            membership_id=member.id,
            starts_on=date(2026, 11, 20),
            ends_on=date(2026, 11, 19),
        )
    )

    with pytest.raises(IntegrityError):
        session.flush()


def test_owner_is_always_active(session: Session) -> None:
    """
    GIVEN nothing yet
    WHEN  an inactive owner is saved, past the service
    THEN  the database refuses it: the owner is always active (FR-63)
    """
    home = homes_service.create_home(
        session, name="Our Flat", area=None, first_month=date(2026, 11, 1)
    )
    person = Person(phone="+8801712345678")
    session.add(person)
    session.flush()

    session.add(
        Membership(
            home_id=home.id,
            person_id=person.id,
            name="Rabbi",
            role=Role.OWNER,
            status=MembershipStatus.INACTIVE,
        )
    )

    with pytest.raises(IntegrityError):
        session.flush()


def test_member_has_one_open_stay(session: Session) -> None:
    """
    GIVEN Maruf has an open stay in "Our Flat" (no end yet)
    WHEN  a second open stay is saved for him, past the service
    THEN  the database refuses it
    """
    home = homes_service.create_home(
        session, name="Our Flat", area=None, first_month=date(2026, 11, 1)
    )
    person = Person(phone="+8801812345678")
    session.add(person)
    session.flush()
    member = Membership(home_id=home.id, person_id=person.id, name="Maruf")
    session.add(member)
    session.flush()
    session.add(
        MembershipPeriod(
            home_id=home.id, membership_id=member.id, starts_on=date(2026, 11, 1)
        )
    )
    session.flush()

    session.add(
        MembershipPeriod(
            home_id=home.id, membership_id=member.id, starts_on=date(2026, 12, 1)
        )
    )

    with pytest.raises(IntegrityError):
        session.flush()


def test_database_allows_one_person_active_in_two_homes(session: Session) -> None:
    """
    GIVEN Maruf is an active member of "Old Flat"
    WHEN  an active membership of "Our Flat" is saved for him, past the service
    THEN  the database accepts it: a person can be active in several homes
    """
    person = Person(phone="+8801812345678")
    session.add(person)
    homes = [
        homes_service.create_home(
            session, name=name, area=None, first_month=date(2026, 11, 1)
        )
        for name in ("Old Flat", "Our Flat")
    ]
    session.flush()

    session.add_all(
        Membership(home_id=home.id, person_id=person.id, name="Maruf") for home in homes
    )
    session.flush()

    active = session.exec(
        select(func.count())
        .select_from(Membership)
        .where(
            Membership.person_id == person.id,
            Membership.status == MembershipStatus.ACTIVE,
        )
    ).one()
    assert active == 2
