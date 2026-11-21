from logging.config import fileConfig

from alembic import context
from sqlalchemy import Connection, create_engine, pool
from sqlmodel import SQLModel

from app.core.config import settings

# Import every module's models here so autogenerate sees them.
from app.modules.accounts import models as accounts_models  # noqa: F401
from app.modules.homes import models as homes_models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def database_url() -> str:
    """The URL to migrate: an explicit sqlalchemy.url, else the app's database."""
    return config.get_main_option("sqlalchemy.url") or settings.database_url


def run_migrations_offline() -> None:
    """Emit SQL for the migrations without connecting (``alembic upgrade --sql``)."""
    context.configure(
        url=database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_on(connection: Connection) -> None:
    """Run the migrations on an open connection."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run the migrations on a shared connection (tests) or a new one."""
    # The test harness passes its own connection (backend/tests/conftest.py).
    shared: Connection | None = config.attributes.get("connection")
    if shared is not None:
        run_migrations_on(shared)
        return

    engine = create_engine(database_url(), poolclass=pool.NullPool)
    with engine.connect() as connection:
        run_migrations_on(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
