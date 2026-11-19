import json
from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from app.core.schemas import StandardResponse
from app.core.utils import get_response_message

JSON_MEDIA_TYPE = "application/json"
# Status codes from here up are errors (4xx, 5xx).
HTTP_ERROR_STATUS = 400


class StandardizedRoute(APIRoute):
    """A route whose JSON result is wrapped in the ``StandardResponse`` envelope."""

    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        """Wrap the default handler so JSON bodies come back inside the envelope.

        Returns:
            The wrapping request handler.
        """
        original_route_handler = super().get_route_handler()

        async def wrapped_route_handler(request: Request) -> Response:
            result = await original_route_handler(request)
            # FastAPI serialises a declared return type into a plain Response
            # with a JSON media type (not a JSONResponse), so check the type.
            if result.media_type != JSON_MEDIA_TYPE:
                return result

            envelope = StandardResponse(
                # An endpoint may answer an error status with data (health: 503).
                success=result.status_code < HTTP_ERROR_STATUS,
                message=get_response_message(request),
                data=json.loads(bytes(result.body)),
            )
            headers = dict(result.headers)
            headers.pop("content-length", None)
            return JSONResponse(
                status_code=result.status_code,
                content=envelope.model_dump(exclude_none=True),
                headers=headers,
            )

        return wrapped_route_handler


class CoreRouter(APIRouter):
    """The router every module uses instead of ``APIRouter``."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs["route_class"] = StandardizedRoute
        super().__init__(*args, **kwargs)
