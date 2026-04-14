from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_profile_service, get_session
from src.services.services import ProfileService, ProfileNotFoundError

router = APIRouter()


@router.delete("/api/v1/profile/{user_id}", status_code=204)
async def delete_profile(
    user_id: str,
    service: ProfileService = Depends(get_profile_service),
    session: AsyncSession = Depends(get_session),
):
    try:
        await service.delete_profile(session, user_id)
    except ProfileNotFoundError:
        raise HTTPException(status_code=404, detail="Profile not found")
