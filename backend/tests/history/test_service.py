from datetime import date

from sqlmodel import Session, select

from app.modules.accounts.models import Membership, Person, Role
from app.modules.history import service
from app.modules.history.models import ChangeAction, ChangeEntity, ChangeLog
from app.modules.homes import service as homes_service


def test_record_change_keeps_who_when_and_old_and_new_values(session: Session) -> None:
    """
    GIVEN the owner of "Our Flat" fixed his own name, with a reason
    WHEN  the change is recorded and the transaction committed
    THEN  the history keeps the home, who, what, how, the old and new values,
          the reason and when
    """
    home = homes_service.create_home(
        session, name="Our Flat", area=None, first_month=date(2026, 11, 1)
    )
    person = Person(phone="+8801712345678")
    session.add(person)
    session.flush()
    owner = Membership(
        home_id=home.id, person_id=person.id, name="Rabbi Hasan", role=Role.OWNER
    )
    session.add(owner)
    session.flush()

    service.record_change(
        session,
        home_id=home.id,
        changed_by=owner.id,
        entity=ChangeEntity.MEMBERSHIP,
        entity_id=owner.id,
        action=ChangeAction.UPDATE,
        old_values={"name": "Rabi"},
        new_values={"name": "Rabbi Hasan"},
        reason="Typo",
    )
    session.commit()

    rows = session.exec(select(ChangeLog)).all()
    assert len(rows) == 1
    row = rows[0]
    assert (
        row.home_id,
        row.changed_by,
        row.entity,
        row.entity_id,
        row.action,
        row.old_values,
        row.new_values,
        row.reason,
    ) == (
        home.id,
        owner.id,
        "membership",
        owner.id,
        "update",
        {"name": "Rabi"},
        {"name": "Rabbi Hasan"},
        "Typo",
    )
    assert row.created_at is not None
