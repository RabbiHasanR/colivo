from pydantic import BaseModel


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
