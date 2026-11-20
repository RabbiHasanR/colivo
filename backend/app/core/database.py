from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import Engine
from sqlmodel import Session, create_engine

from app.core.config import settings


def create_database_engine(url: str) -> Engine:
    """Create the engine the app uses for ``url``.

    Args:
        url: A SQLAlchemy database URL.

    Returns:
        The engine.
    """
    return create_engine(
        url,
        pool_pre_ping=True,
        connect_args={"connect_timeout": settings.connect_timeout_seconds},
    )


engine = create_database_engine(settings.database_url)


def get_session() -> Iterator[Session]:
    """Yield a database session for one request and close it afterwards.

    Used as a FastAPI dependency (``Depends(get_session)``); services commit
    explicitly.

    Yields:
        A SQLModel session bound to the application engine.
    """
    with Session(engine) as session:
        yield session


# The database session for an endpoint: `session: SessionDep`.
SessionDep = Annotated[Session, Depends(get_session)]
