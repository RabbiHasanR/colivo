from pathlib import Path
from typing import Annotated, Literal

from pydantic import BeforeValidator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

# The repo-root .env (shared with compose.yaml). Missing inside the container,
# where compose.yaml passes the values as environment variables instead.
ROOT_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


def split_comma_list(value: object) -> object:
    """Split a comma-separated env value into a list of trimmed, non-empty items.

    Args:
        value: The raw value; a string from the environment, or an already
            parsed list.

    Returns:
        A list of strings when ``value`` is a string, otherwise ``value`` as is.
    """
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return value


class Settings(BaseSettings):
    """Backend settings, read from environment variables and the root .env."""

    model_config = SettingsConfigDict(env_file=ROOT_ENV_FILE, extra="ignore")

    project_name: str = "Colivo"
    environment: Literal["development", "test", "production"] = "development"

    database_url: str
    # Only the test suite uses it; tests refuse to run without it.
    test_database_url: str | None = None
    redis_url: str
    # How long any connection to PostgreSQL or Redis may take before it counts
    # as down. Whole seconds: libpq's connect_timeout takes an integer.
    connect_timeout_seconds: int = 2

    backend_cors_origins: Annotated[
        list[str], NoDecode, BeforeValidator(split_comma_list)
    ] = []


settings = Settings()  # pyright: ignore[reportCallIssue]  (values come from the environment)
