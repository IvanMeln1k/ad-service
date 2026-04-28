from fastapi import APIRouter, Depends

from src.dependencies import get_registration_service
from src.schemas.schemas import LogoutRequest
from src.services.service import RegistrationService

router = APIRouter()


@router.post("/api/v1/logout", status_code=200)
async def logout(
    request: LogoutRequest,
    service: RegistrationService = Depends(get_registration_service),
):
    await service.logout(request.user_id, request.refresh_token)
    return {"status": "ok"}
