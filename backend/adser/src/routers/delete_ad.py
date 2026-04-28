from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import get_current_user, AuthUser
from src.dependencies import get_ads_service, get_session
from src.services.service import AdsService, AdNotFoundError, NotOwnerError, AdBannedError

router = APIRouter()


@router.delete("/api/v1/ads/{ad_id}", status_code=204)
async def delete_ad(
    ad_id: str,
    user: AuthUser = Depends(get_current_user),
    service: AdsService = Depends(get_ads_service),
    session: AsyncSession = Depends(get_session),
):
    try:
        await service.delete_ad(session, ad_id, user.user_id)
    except AdNotFoundError:
        raise HTTPException(status_code=404, detail="Ad not found")
    except NotOwnerError:
        raise HTTPException(status_code=403, detail="Not the owner")
    except AdBannedError:
        raise HTTPException(status_code=403, detail="Cannot delete a banned ad")
