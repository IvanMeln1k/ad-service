from fastapi import APIRouter, Depends, HTTPException

from src.dependencies import get_registration_service
from src.schemas.schemas import ConfirmEmailRequest
from src.services.service import RegistrationService, InvalidTokenError, EmailAlreadyTakenError

router = APIRouter()


@router.post("/api/v1/confirm-email")
async def confirm_email(
    request: ConfirmEmailRequest,
    service: RegistrationService = Depends(get_registration_service),
):
    try:
        await service.confirm_email(request.token)
        return {"status": "confirmed"}
    except InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    except EmailAlreadyTakenError:
        raise HTTPException(status_code=409, detail="Email already confirmed")
