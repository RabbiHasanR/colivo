from pathlib import Path
from typing import Annotated, Literal, Self

from pydantic import BeforeValidator, model_validator
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
    # Only the test suite uses it. Unset: tests use database 15 of REDIS_URL's
    # server, and refuse to run on REDIS_URL's own database.
    test_redis_url: str | None = None
    # How long any connection to PostgreSQL or Redis may take before it counts
    # as down. Whole seconds: libpq's connect_timeout takes an integer.
    connect_timeout_seconds: int = 2

    backend_cors_origins: Annotated[
        list[str], NoDecode, BeforeValidator(split_comma_list)
    ] = []

    # Send the session cookie over HTTPS only. Safe by default; .env turns it
    # off for http://localhost in development.
    session_cookie_secure: bool = True
    # How SMS and email reach people. Only "log" exists until a provider is
    # chosen (specs/tech-stack.md → Deferred decisions).
    notifier: Literal["log"] = "log"

    @model_validator(mode="after")
    def refuse_the_log_notifier_in_production(self) -> Self:
        """Never run production with the development notifier.

        It logs every one-time code in plain text, so anyone who can read the
        logs could log in as anyone (security review, 21 Nov 2026).

        Returns:
            The settings, unchanged.

        Raises:
            ValueError: In production with ``NOTIFIER=log``.
        """
        if self.environment == "production" and self.notifier == "log":
            raise ValueError(
                "NOTIFIER=log logs one-time codes in plain text; "
                "production needs a real SMS and email notifier."
            )
        return self


settings = Settings()  # pyright: ignore[reportCallIssue]  (values come from the environment)
