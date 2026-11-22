from pydantic import BaseModel


class SetupStep(BaseModel):
    """One step of the new-home checklist (FR-95)."""

    key: str
    done: bool


class SetupOut(BaseModel):
    """The new-home checklist, in order."""

    steps: list[SetupStep]
