from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import get_current_user, AuthUser
from src.dependencies import get_ads_service, get_session
from src.schemas.schemas import BanRequest, BanResponse
from src.services.service import AdsService, AdNotFoundError

router = APIRouter()


@router.post("/api/v1/ads/{ad_id}/ban", response_model=BanResponse)
async def ban_ad(
    ad_id: str,
    request: BanRequest,
    user: AuthUser = Depends(get_current_user),
    service: AdsService = Depends(get_ads_service),
    session: AsyncSession = Depends(get_session),
):
    if "MODERATOR" not in user.roles and "ADMIN" not in user.roles:
        raise HTTPException(status_code=403, detail="Moderator role required")
    try:
        ban = await service.ban_ad(session, ad_id, user.user_id, request.reason)
        return BanResponse(
            id=ban.id, ad_id=ban.ad_id, moderator_id=ban.moderator_id,
            reason=ban.reason, banned_at=ban.banned_at,
        )
    except AdNotFoundError:
        raise HTTPException(status_code=404, detail="Ad not found")
