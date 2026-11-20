from enum import StrEnum

from pydantic import BaseModel


class ServiceStatus(StrEnum):
    """Whether a dependency of the backend answered."""

    OK = "ok"
    DOWN = "down"


class HealthOut(BaseModel):
    """The status of each dependency the backend needs."""

    database: ServiceStatus
    redis: ServiceStatus
