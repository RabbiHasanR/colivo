from fastapi import Request, Response

from app.api.deps import OwnerOrManagerDep
from app.core.database import SessionDep
from app.core.router import CoreRouter
from app.core.utils import set_response_message
from app.modules.homes import service
from app.modules.homes.schemas import SetupOut

router = CoreRouter()


@router.get("/home/setup")
def get_setup(
    request: Request,
    response: Response,
    membership: OwnerOrManagerDep,
    session: SessionDep,
) -> SetupOut:
    """The setup checklist of the logged-in owner's or manager's home."""
    set_response_message(request, "Setup checklist")
    response.status_code = 200
    return service.get_setup(session, membership.home_id)
