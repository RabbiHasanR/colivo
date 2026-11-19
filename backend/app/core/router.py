import json
from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from app.core.schemas import StandardResponse
from app.core.utils import get_response_message


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
            if not isinstance(result, JSONResponse):
                return result

            envelope = StandardResponse(
                success=True,
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
