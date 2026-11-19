from collections.abc import Iterator

from sqlmodel import Session, create_engine

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)


def get_session() -> Iterator[Session]:
    """Yield a database session for one request and close it afterwards.

    Used as a FastAPI dependency (``Depends(get_session)``); services commit
    explicitly.

    Yields:
        A SQLModel session bound to the application engine.
    """
    with Session(engine) as session:
        yield session
