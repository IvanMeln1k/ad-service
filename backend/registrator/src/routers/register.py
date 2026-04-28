from fastapi import APIRouter, Depends, HTTPException

from src.dependencies import get_registration_service
from src.schemas.schemas import RegisterRequest, RegisterResponse, TokenInfo
from src.services.service import RegistrationService, EmailAlreadyTakenError

router = APIRouter()


@router.post("/api/v1/register", response_model=RegisterResponse, status_code=201)
async def register(
    request: RegisterRequest,
    service: RegistrationService = Depends(get_registration_service),
):
    try:
        result = await service.register(request.email, request.name, request.password)
        return RegisterResponse(
            user_id=result.user_id,
            access_token=result.access_token,
            refresh_token=TokenInfo(
                token=result.refresh_token,
                expires_at=result.refresh_token_expires_at,
            ),
        )
    except EmailAlreadyTakenError:
        raise HTTPException(status_code=409, detail="Email already taken")
