from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.schemas import StandardResponse


def error_response(status_code: int, message: str, errors: list[str]) -> JSONResponse:
    """Build an error response inside the ``StandardResponse`` envelope.

    Args:
        status_code: The HTTP status code.
        message: A short, user-facing message.
        errors: Error details, one string each.

    Returns:
        The JSON response.
    """
    body = StandardResponse(success=False, message=message, errors=errors)
    return JSONResponse(
        status_code=status_code, content=body.model_dump(exclude_none=True)
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Answer an HTTP error (404, 403, a service's 400 …) in the envelope.

    Args:
        request: The current request.
        exc: The raised HTTP exception.

    Returns:
        The error response.
    """
    detail = exc.detail if isinstance(exc.detail, str) else "Request failed"
    return error_response(exc.status_code, detail, [detail])


def register_exception_handlers(app: FastAPI) -> None:
    """Give every error the ``StandardResponse`` shape.

    Args:
        app: The FastAPI app.
    """
    # Starlette types handlers as taking any Exception; ours takes the subclass
    # it is registered for, which is safe.
    app.add_exception_handler(
        StarletteHTTPException,
        http_exception_handler,  # pyright: ignore[reportArgumentType]
    )
