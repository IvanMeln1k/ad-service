from fastapi import APIRouter, Depends, HTTPException

from src.dependencies import get_registration_service
from src.schemas.schemas import LoginRequest, LoginResponse, TokenInfo
from src.services.service import RegistrationService, InvalidCredentialsError

router = APIRouter()


@router.post("/api/v1/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    service: RegistrationService = Depends(get_registration_service),
):
    try:
        result = await service.login(request.email, request.password)
        return LoginResponse(
            user_id=result.user_id,
            access_token=result.access_token,
            refresh_token=TokenInfo(
                token=result.refresh_token,
                expires_at=result.refresh_token_expires_at,
            ),
        )
    except InvalidCredentialsError:
        raise HTTPException(status_code=401, detail="Invalid email or password")
