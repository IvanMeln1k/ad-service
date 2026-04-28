from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_profile_service, get_session, require_staff
from src.schemas.schemas import ProfileResponse, RoleResponse
from src.services.services import ProfileService

router = APIRouter()


@router.get("/api/v1/profile", response_model=list[ProfileResponse])
async def list_profiles(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: set[str] = Depends(require_staff),
    service: ProfileService = Depends(get_profile_service),
    session: AsyncSession = Depends(get_session),
):
    profiles = await service.list_profiles(session, limit, offset)
    return [
        ProfileResponse(
            user_id=p.user_id,
            name=p.name,
            city=p.city,
            email=p.email,
            email_confirmed=p.email_confirmed,
            avatar_url=p.avatar_url,
            roles=[RoleResponse(role=r.role, assigned_at=r.assigned_at) for r in p.roles],
            created_at=p.created_at,
        )
        for p in profiles
    ]
