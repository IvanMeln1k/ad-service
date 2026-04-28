from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import get_current_user, AuthUser
from src.dependencies import get_ads_service, get_session
from src.schemas.schemas import UnbanRequest
from src.services.service import AdsService, AdNotFoundError

router = APIRouter()


@router.post("/api/v1/ads/{ad_id}/unban")
async def unban_ad(
    ad_id: str,
    request: UnbanRequest,
    user: AuthUser = Depends(get_current_user),
    service: AdsService = Depends(get_ads_service),
    session: AsyncSession = Depends(get_session),
):
    if "MODERATOR" not in user.roles and "ADMIN" not in user.roles:
        raise HTTPException(status_code=403, detail="Moderator role required")
    try:
        await service.unban_ad(session, ad_id, user.user_id, request.unban_reason)
        return {"status": "unbanned"}
    except AdNotFoundError:
        raise HTTPException(status_code=404, detail="Ad or active ban not found")
