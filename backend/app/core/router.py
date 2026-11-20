import json
from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import APIRouter, Request, Response
from fastapi.dependencies.utils import get_typed_return_annotation
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from app.core.schemas import StandardResponse
from app.core.utils import get_response_message

JSON_MEDIA_TYPE = "application/json"
# Status codes from here up are errors (4xx, 5xx).
HTTP_ERROR_STATUS = 400


class StandardizedRoute(APIRoute):
    """A route whose JSON result is wrapped in the ``StandardResponse`` envelope."""

    def __init__(self, path: str, endpoint: Callable[..., Any], **kwargs: Any) -> None:
        # Declare the wrapped shape in OpenAPI for the success status, so the
        # generated clients see what is really sent. FastAPI documents
        # `responses` as *merged* with the return model's schema; replacing the
        # schema this way relies on that merge, so test T6.1
        # (tests/core/test_api.py) pins it and fails if an upgrade changes it.
        data_model = get_typed_return_annotation(endpoint)
        if data_model is not None:
            success_status = kwargs.get("status_code") or 200
            kwargs["responses"] = {
                success_status: {"model": StandardResponse[data_model]},
                **(kwargs.get("responses") or {}),
            }
        super().__init__(path, endpoint, **kwargs)

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

            envelope = StandardResponse[Any](
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
