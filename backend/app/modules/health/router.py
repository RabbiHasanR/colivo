from fastapi import Request, Response

from app.core.database import SessionDep
from app.core.redis import RedisDep
from app.core.router import CoreRouter
from app.core.schemas import StandardResponse
from app.core.utils import set_response_message
from app.modules.health import service
from app.modules.health.schemas import HealthOut

router = CoreRouter()


@router.get(
    "/health",
    responses={503: {"model": StandardResponse[HealthOut]}},
)
def get_health(
    request: Request,
    response: Response,
    session: SessionDep,
    redis_client: RedisDep,
) -> HealthOut:
    """Report whether the backend can reach the database and Redis."""
    health = service.get_health(session, redis_client)
    if service.is_healthy(health):
        set_response_message(request, "Healthy")
        response.status_code = 200
    else:
        set_response_message(request, "Service unavailable")
        response.status_code = 503
    return health
