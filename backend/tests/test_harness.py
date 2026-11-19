from sqlalchemy import make_url, text
from sqlmodel import Session

from app.core.config import settings


def test_tests_run_against_the_test_database(session: Session) -> None:
    """
    GIVEN the test session fixture
    WHEN  it asks PostgreSQL which database it is connected to
    THEN  it is the database in TEST_DATABASE_URL, never the app's own
    """
    assert settings.test_database_url is not None
    current = session.connection().execute(text("SELECT current_database()"))

    assert current.scalar_one() == make_url(settings.test_database_url).database
