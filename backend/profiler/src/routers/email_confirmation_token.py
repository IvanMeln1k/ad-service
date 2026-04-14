from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_email_service, get_session
from src.schemas.schemas import EmailConfirmationTokenResponse
from src.services.services import EmailConfirmationService, ProfileNotFoundError

router = APIRouter()


@router.get(
    "/api/v1/profile/{user_id}/email-confirmation-token",
    response_model=EmailConfirmationTokenResponse,
)
async def get_email_confirmation_token(
    user_id: str,
    service: EmailConfirmationService = Depends(get_email_service),
    session: AsyncSession = Depends(get_session),
):
    try:
        token = await service.create_email_confirmation_token(session, user_id)
        return EmailConfirmationTokenResponse(token=token)
    except ProfileNotFoundError:
        raise HTTPException(status_code=404, detail="Profile not found")
