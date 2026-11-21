import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.schemas import StandardResponse

logger = logging.getLogger(__name__)

# What a client sees for an unexpected error. The details go to the server log.
UNEXPECTED_ERROR_MESSAGE = "An unexpected error occurred."
VALIDATION_ERROR_MESSAGE = "Validation Error"


def error_response(status_code: int, message: str, errors: list[str]) -> JSONResponse:
    """Build an error response inside the ``StandardResponse`` envelope.

    Args:
        status_code: The HTTP status code.
        message: A short, user-facing message.
        errors: Error details, one string each.

    Returns:
        The JSON response.
    """
    body = StandardResponse[None](success=False, message=message, errors=errors)
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


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Answer invalid input with 422 in the envelope.

    Each problem becomes one ``"<location>: <message>"`` string, e.g.
    ``"body.name: Field required"``; the web's ``errors.ts`` reads them back
    into field errors.

    Args:
        request: The current request.
        exc: The validation error.

    Returns:
        The error response.
    """
    errors = [
        f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
        for error in exc.errors()
    ]
    return error_response(422, VALIDATION_ERROR_MESSAGE, errors)


async def unexpected_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Answer any unhandled error with a generic 500, never its details.

    The exception (message, traceback) is logged on the server only: it can
    hold SQL, addresses or secrets.

    Args:
        request: The current request.
        exc: The unhandled exception.

    Returns:
        The error response.
    """
    logger.error(
        "Unhandled error on %s %s",
        request.method,
        request.url.path,
        exc_info=exc,
    )
    return error_response(500, "Internal Server Error", [UNEXPECTED_ERROR_MESSAGE])


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
    app.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,  # pyright: ignore[reportArgumentType]
    )
    app.add_exception_handler(Exception, unexpected_exception_handler)
