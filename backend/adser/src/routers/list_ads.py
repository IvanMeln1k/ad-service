from typing import Optional, Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import get_optional_user, AuthUser
from src.dependencies import get_ads_service, get_session
from src.schemas.schemas import AdResponse, PhotoResponse, AdsListResponse
from src.services.service import AdsService

router = APIRouter()


@router.get("/api/v1/ads", response_model=AdsListResponse)
async def list_ads(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None, min_length=1, max_length=100),
    category: Optional[str] = Query(None),
    city: Optional[str] = Query(None, min_length=2, max_length=255),
    price_min: Optional[float] = Query(None, ge=0),
    price_max: Optional[float] = Query(None, ge=0),
    sort_by: Literal["created_at", "price", "title"] = Query("created_at"),
    sort_order: Literal["asc", "desc"] = Query("desc"),
    service: AdsService = Depends(get_ads_service),
    session: AsyncSession = Depends(get_session),
    user: Optional[AuthUser] = Depends(get_optional_user),
):
    if price_min is not None and price_max is not None and price_min > price_max:
        from fastapi import HTTPException

        raise HTTPException(status_code=422, detail="price_min must be <= price_max")

    include_banned = user is not None and (
        "MODERATOR" in user.roles or "ADMIN" in user.roles
    )
    ads, total = await service.list_ads(
        session=session,
        limit=limit,
        offset=offset,
        search=search,
        include_banned=include_banned,
        category=category,
        city=city,
        price_min=price_min,
        price_max=price_max,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return AdsListResponse(
        items=[
            AdResponse(
            id=a.id, user_id=a.user_id, title=a.title, description=a.description,
            price=a.price, city=a.city, category=a.category,
            status=a.status, is_banned=a.is_banned, ban_reason=a.ban_reason,
            photos=[PhotoResponse(id=p.id, s3_key=p.s3_key, position=p.position) for p in a.photos],
            created_at=a.created_at, updated_at=a.updated_at,
        )
        for a in ads
        ],
        total=total,
        limit=limit,
        offset=offset,
    )
