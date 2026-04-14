from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_email_service, get_session
from src.schemas.schemas import ConfirmEmailRequest
from src.services.services import (
    EmailConfirmationService,
    InvalidConfirmationTokenError,
    ExpiredConfirmationTokenError,
    EmailAlreadyConfirmedError,
)

router = APIRouter()


@router.post("/api/v1/email-confirmation")
async def confirm_email(
    request: ConfirmEmailRequest,
    service: EmailConfirmationService = Depends(get_email_service),
    session: AsyncSession = Depends(get_session),
):
    try:
        await service.confirm_email(session, request.token)
        return {"status": "confirmed"}
    except InvalidConfirmationTokenError:
        raise HTTPException(status_code=400, detail="Invalid token")
    except ExpiredConfirmationTokenError:
        raise HTTPException(status_code=400, detail="Token expired")
    except EmailAlreadyConfirmedError:
        raise HTTPException(status_code=409, detail="Email already confirmed")
