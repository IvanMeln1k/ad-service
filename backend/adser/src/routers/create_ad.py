from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import get_current_user, AuthUser
from src.dependencies import get_ads_service, get_session
from src.schemas.schemas import CreateAdRequest, AdResponse
from src.services.service import AdsService

router = APIRouter()


@router.post("/api/v1/ads", response_model=AdResponse, status_code=201)
async def create_ad(
    request: CreateAdRequest,
    user: AuthUser = Depends(get_current_user),
    service: AdsService = Depends(get_ads_service),
    session: AsyncSession = Depends(get_session),
):
    if not user.email_confirmed:
        raise HTTPException(status_code=403, detail="Email not confirmed")
    if "MODERATOR" in user.roles or "ADMIN" in user.roles:
        raise HTTPException(status_code=403, detail="Staff users cannot create ads")
    ad = await service.create_ad(
        session=session,
        user_id=user.user_id,
        title=request.title,
        description=request.description,
        price=request.price,
        city=request.city,
        category=request.category,
    )
    return AdResponse(
        id=ad.id, user_id=ad.user_id, title=ad.title, description=ad.description,
        price=ad.price, city=ad.city, category=ad.category,
        status=ad.status, created_at=ad.created_at, updated_at=ad.updated_at,
    )
