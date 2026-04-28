from fastapi import APIRouter, Depends, HTTPException

from src.dependencies import get_notification_service
from src.schemas.schemas import SendEmailRequest, SendEmailResponse
from src.services.service import NotificationService, SendError

router = APIRouter()


@router.post("/api/v1/notifications/email", response_model=SendEmailResponse)
async def send_email(
    request: SendEmailRequest,
    service: NotificationService = Depends(get_notification_service),
):
    try:
        await service.send_email(request.to, request.subject, request.body)
        return SendEmailResponse(status="sent")
    except SendError as e:
        raise HTTPException(status_code=502, detail=str(e))
