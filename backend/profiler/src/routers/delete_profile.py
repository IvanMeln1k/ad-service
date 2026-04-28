from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import AuthUser, get_current_user
from src.dependencies import get_profile_service, get_session, get_current_user_roles
from src.services.services import ProfileService, ProfileNotFoundError

router = APIRouter()


@router.delete("/api/v1/profile/{user_id}", status_code=204)
async def delete_profile(
    user_id: str,
    user: AuthUser = Depends(get_current_user),
    current_roles: set[str] = Depends(get_current_user_roles),
    service: ProfileService = Depends(get_profile_service),
    session: AsyncSession = Depends(get_session),
):
    is_admin = "ADMIN" in current_roles
    if user.user_id != user_id and not is_admin:
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    try:
        await service.delete_profile(session, user_id)
    except ProfileNotFoundError:
        raise HTTPException(status_code=404, detail="Profile not found")
