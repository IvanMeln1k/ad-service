from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_ads_service, get_session, get_profiler_client
from src.clients.profiler_client import ProfilerClient
from src.schemas.schemas import AdResponse, PhotoResponse, AuthorResponse
from src.services.service import AdsService, AdNotFoundError

router = APIRouter()


@router.get("/api/v1/ads/{ad_id}", response_model=AdResponse)
async def get_ad(
    ad_id: str,
    service: AdsService = Depends(get_ads_service),
    session: AsyncSession = Depends(get_session),
    profiler: ProfilerClient = Depends(get_profiler_client),
):
    try:
        a = await service.get_ad(session, ad_id)
    except AdNotFoundError:
        raise HTTPException(status_code=404, detail="Ad not found")

    author = None
    profile = await profiler.get_profile(a.user_id)
    if profile:
        author = AuthorResponse(
            user_id=profile.user_id,
            name=profile.name,
            email=profile.email,
            city=profile.city,
            avatar_url=profile.avatar_url,
        )

    return AdResponse(
        id=a.id, user_id=a.user_id, title=a.title, description=a.description,
        price=a.price, city=a.city, category=a.category,
        status=a.status, is_banned=a.is_banned, ban_reason=a.ban_reason,
        photos=[PhotoResponse(id=p.id, s3_key=p.s3_key, position=p.position) for p in a.photos],
        author=author,
        created_at=a.created_at, updated_at=a.updated_at,
    )
