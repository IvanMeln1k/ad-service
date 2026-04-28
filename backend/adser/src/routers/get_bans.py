from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import get_current_user, AuthUser
from src.dependencies import get_ads_service, get_session
from src.schemas.schemas import BanResponse
from src.services.service import AdsService, AdNotFoundError

router = APIRouter()


@router.get("/api/v1/ads/{ad_id}/bans", response_model=list[BanResponse])
async def get_bans(
    ad_id: str,
    user: AuthUser = Depends(get_current_user),
    service: AdsService = Depends(get_ads_service),
    session: AsyncSession = Depends(get_session),
):
    if "MODERATOR" not in user.roles and "ADMIN" not in user.roles:
        raise HTTPException(status_code=403, detail="Moderator role required")
    try:
        bans = await service.get_bans(session, ad_id)
        return [
            BanResponse(
                id=b.id, ad_id=b.ad_id, moderator_id=b.moderator_id, reason=b.reason,
                banned_at=b.banned_at, unbanned_by_id=b.unbanned_by_id,
                unban_reason=b.unban_reason, unbanned_at=b.unbanned_at,
            )
            for b in bans
        ]
    except AdNotFoundError:
        raise HTTPException(status_code=404, detail="Ad not found")
