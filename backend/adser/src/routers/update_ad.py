from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import get_current_user, AuthUser
from src.dependencies import get_ads_service, get_session
from src.schemas.schemas import UpdateAdRequest, AdResponse, PhotoResponse
from src.services.service import AdsService, AdNotFoundError, NotOwnerError

router = APIRouter()


@router.patch("/api/v1/ads/{ad_id}", response_model=AdResponse)
async def update_ad(
    ad_id: str,
    request: UpdateAdRequest,
    user: AuthUser = Depends(get_current_user),
    service: AdsService = Depends(get_ads_service),
    session: AsyncSession = Depends(get_session),
):
    try:
        a = await service.update_ad(
            session=session,
            ad_id=ad_id,
            user_id=user.user_id,
            title=request.title,
            description=request.description,
            price=request.price,
            city=request.city,
            category=request.category,
        )
        return AdResponse(
            id=a.id, user_id=a.user_id, title=a.title, description=a.description,
            price=a.price, city=a.city, category=a.category,
            status=a.status, is_banned=a.is_banned,
            photos=[PhotoResponse(id=p.id, s3_key=p.s3_key, position=p.position) for p in a.photos],
            created_at=a.created_at, updated_at=a.updated_at,
        )
    except AdNotFoundError:
        raise HTTPException(status_code=404, detail="Ad not found")
    except NotOwnerError:
        raise HTTPException(status_code=403, detail="Not the owner")
