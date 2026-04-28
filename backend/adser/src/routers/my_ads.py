from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import get_current_user, AuthUser
from src.dependencies import get_ads_service, get_session
from src.schemas.schemas import AdResponse, PhotoResponse
from src.services.service import AdsService

router = APIRouter()


@router.get("/api/v1/ads/my", response_model=list[AdResponse])
async def my_ads(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: AuthUser = Depends(get_current_user),
    service: AdsService = Depends(get_ads_service),
    session: AsyncSession = Depends(get_session),
):
    ads = await service.list_user_ads(session, user.user_id, limit, offset)
    return [
        AdResponse(
            id=a.id, user_id=a.user_id, title=a.title, description=a.description,
            price=a.price, city=a.city, category=a.category,
            status=a.status, is_banned=a.is_banned, ban_reason=a.ban_reason,
            photos=[PhotoResponse(id=p.id, s3_key=p.s3_key, position=p.position) for p in a.photos],
            created_at=a.created_at, updated_at=a.updated_at,
        )
        for a in ads
    ]
