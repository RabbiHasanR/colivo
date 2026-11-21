from fastapi import Request, Response

from app.api.deps import CurrentMemberDep
from app.core.router import CoreRouter
from app.core.utils import set_response_message
from app.modules.homes.schemas import SetupOut

router = CoreRouter()


@router.get("/home/setup")
def get_setup(
    request: Request, response: Response, membership: CurrentMemberDep
) -> SetupOut:
    """The setup checklist of the logged-in member's home."""
    set_response_message(request, "Setup checklist")
    response.status_code = 200
    return SetupOut(steps=[])
