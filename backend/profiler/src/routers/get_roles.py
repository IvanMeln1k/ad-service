from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import AuthUser, get_current_user
from src.dependencies import get_roles_service, get_session, get_current_user_roles
from src.schemas.schemas import RoleResponse
from src.services.services import RolesService

router = APIRouter()


@router.get("/api/v1/profile/{user_id}/roles", response_model=list[RoleResponse])
async def get_roles(
    user_id: str,
    user: AuthUser = Depends(get_current_user),
    current_roles: set[str] = Depends(get_current_user_roles),
    service: RolesService = Depends(get_roles_service),
    session: AsyncSession = Depends(get_session),
):
    is_staff = "ADMIN" in current_roles or "MODERATOR" in current_roles
    if user.user_id != user_id and not is_staff:
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    roles = await service.get_roles(session, user_id)
    return [RoleResponse(role=r.role, assigned_at=r.assigned_at) for r in roles]
