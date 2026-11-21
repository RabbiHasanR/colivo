import pytest
from pydantic import ValidationError

from app.core.config import Settings

DATABASE_URL = "postgresql+psycopg://colivo@db.example/colivo"
REDIS_URL = "redis://redis.example:6379/0"


def test_production_refuses_the_development_notifier() -> None:
    """
    GIVEN the development notifier, which logs every one-time code in plain text
    WHEN  the backend's settings load for production, and for development
    THEN  production refuses to start with it; development starts
    """
    development = Settings(
        environment="development",
        notifier="log",
        database_url=DATABASE_URL,
        redis_url=REDIS_URL,
    )

    with pytest.raises(ValidationError, match="NOTIFIER=log"):
        Settings(
            environment="production",
            notifier="log",
            database_url=DATABASE_URL,
            redis_url=REDIS_URL,
        )

    assert development.notifier == "log"
