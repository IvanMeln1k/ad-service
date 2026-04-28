from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_roles_service, get_session, require_admin
from src.schemas.schemas import UpdateRoleRequest, RoleResponse
from src.services.services import RolesService, ProfileNotFoundError, InvalidRoleError

router = APIRouter()


@router.post("/api/v1/profile/{user_id}/roles", response_model=list[RoleResponse])
async def assign_role(
    user_id: str,
    request: UpdateRoleRequest,
    _: set[str] = Depends(require_admin),
    service: RolesService = Depends(get_roles_service),
    session: AsyncSession = Depends(get_session),
):
    try:
        roles = await service.assign_role(session, user_id, request.role)
        return [RoleResponse(role=r.role, assigned_at=r.assigned_at) for r in roles]
    except ProfileNotFoundError:
        raise HTTPException(status_code=404, detail="Profile not found")
    except InvalidRoleError:
        raise HTTPException(status_code=422, detail="Unsupported role")


@router.delete("/api/v1/profile/{user_id}/roles", response_model=list[RoleResponse])
async def remove_role(
    user_id: str,
    request: UpdateRoleRequest,
    _: set[str] = Depends(require_admin),
    service: RolesService = Depends(get_roles_service),
    session: AsyncSession = Depends(get_session),
):
    try:
        roles = await service.remove_role(session, user_id, request.role)
        return [RoleResponse(role=r.role, assigned_at=r.assigned_at) for r in roles]
    except ProfileNotFoundError:
        raise HTTPException(status_code=404, detail="Profile not found")
    except InvalidRoleError:
        raise HTTPException(status_code=422, detail="Unsupported role")
