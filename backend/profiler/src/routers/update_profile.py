from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_profile_service, get_session
from src.schemas.schemas import UpdateProfileRequest, ProfileResponse, RoleResponse
from src.services.services import ProfileService, ProfileNotFoundError

router = APIRouter()


@router.patch("/api/v1/profile/{user_id}", response_model=ProfileResponse)
async def update_profile(
    user_id: str,
    request: UpdateProfileRequest,
    service: ProfileService = Depends(get_profile_service),
    session: AsyncSession = Depends(get_session),
):
    try:
        p = await service.update_profile(session, user_id, name=request.name, city=request.city)
        return ProfileResponse(
            user_id=p.user_id,
            name=p.name,
            city=p.city,
            email=p.email,
            email_confirmed=p.email_confirmed,
            avatar_url=p.avatar_url,
            roles=[RoleResponse(role=r.role, assigned_at=r.assigned_at) for r in p.roles],
            created_at=p.created_at,
        )
    except ProfileNotFoundError:
        raise HTTPException(status_code=404, detail="Profile not found")
