from typing import Annotated

from pydantic import BaseModel, StringConstraints

# A name or short label: trimmed, 1 to 80 characters. Matches the database's
# `CHECK` on names (specs/data-model.md → Tables).
SHORT_TEXT_MAX = 80
ShortText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=SHORT_TEXT_MAX),
]


class StandardResponse[T](BaseModel):
    """The envelope around every API response (specs/tech-stack.md).

    ``StandardResponse[HealthOut]`` is what an endpoint returning ``HealthOut``
    really sends; ``CoreRouter`` declares it in OpenAPI. Empty fields are left
    out when serialised (``exclude_none``).
    """

    success: bool
    message: str
    data: T | None = None
    errors: list[str] | None = None
