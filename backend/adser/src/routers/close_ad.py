from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import get_current_user, AuthUser
from src.dependencies import get_ads_service, get_session
from src.services.service import AdsService, AdNotFoundError, NotOwnerError, AdAlreadyClosedError, AdBannedError

router = APIRouter()


@router.post("/api/v1/ads/{ad_id}/close")
async def close_ad(
    ad_id: str,
    user: AuthUser = Depends(get_current_user),
    service: AdsService = Depends(get_ads_service),
    session: AsyncSession = Depends(get_session),
):
    try:
        await service.close_ad(session, ad_id, user.user_id)
        return {"status": "closed"}
    except AdNotFoundError:
        raise HTTPException(status_code=404, detail="Ad not found")
    except NotOwnerError:
        raise HTTPException(status_code=403, detail="Not the owner")
    except AdBannedError:
        raise HTTPException(status_code=403, detail="Cannot close a banned ad")
    except AdAlreadyClosedError:
        raise HTTPException(status_code=409, detail="Ad is already closed")
