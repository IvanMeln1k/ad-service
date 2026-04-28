from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import get_current_user, AuthUser
from src.dependencies import get_ads_service, get_session
from src.services.service import AdsService, AdNotFoundError, NotOwnerError

router = APIRouter()


@router.delete("/api/v1/ads/{ad_id}/photos/{photo_id}", status_code=204)
async def delete_photo(
    ad_id: str,
    photo_id: str,
    user: AuthUser = Depends(get_current_user),
    service: AdsService = Depends(get_ads_service),
    session: AsyncSession = Depends(get_session),
):
    try:
        await service.delete_photo(session, ad_id, user.user_id, photo_id)
    except AdNotFoundError:
        raise HTTPException(status_code=404, detail="Ad or photo not found")
    except NotOwnerError:
        raise HTTPException(status_code=403, detail="Not the owner")
