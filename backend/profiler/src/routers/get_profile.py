from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_profile_service, get_session
from src.schemas.schemas import ProfileResponse, RoleResponse
from src.services.services import ProfileService, ProfileNotFoundError

router = APIRouter()


@router.get("/api/v1/profile/{user_id}", response_model=ProfileResponse)
async def get_profile(
    user_id: str,
    service: ProfileService = Depends(get_profile_service),
    session: AsyncSession = Depends(get_session),
):
    try:
        p = await service.get_profile(session, user_id)
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
