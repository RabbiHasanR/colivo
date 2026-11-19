from typing import Any

from pydantic import BaseModel


class StandardResponse(BaseModel):
    """The envelope around every API response (specs/tech-stack.md).

    Empty fields are left out when serialised (``exclude_none``).
    """

    success: bool
    message: str
    data: Any | None = None
    errors: list[str] | None = None
