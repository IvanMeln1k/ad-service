from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_profile_service, get_session
from src.schemas.schemas import ProfileLookupItem
from src.services.services import ProfileService

router = APIRouter()


@router.get("/api/v1/profile/lookup", response_model=list[ProfileLookupItem])
async def lookup_by_email(
    email: str = Query(...),
    service: ProfileService = Depends(get_profile_service),
    session: AsyncSession = Depends(get_session),
):
    results = await service.find_profiles_by_email(session, email)
    return [
        ProfileLookupItem(
            user_id=r.user_id,
            name=r.name,
            avatar_url=r.avatar_url,
        )
        for r in results
    ]
