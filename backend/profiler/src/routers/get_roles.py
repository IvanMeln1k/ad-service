from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_roles_service, get_session
from src.schemas.schemas import RoleResponse
from src.services.services import RolesService

router = APIRouter()


@router.get("/api/v1/profile/{user_id}/roles", response_model=list[RoleResponse])
async def get_roles(
    user_id: str,
    service: RolesService = Depends(get_roles_service),
    session: AsyncSession = Depends(get_session),
):
    roles = await service.get_roles(session, user_id)
    return [RoleResponse(role=r.role, assigned_at=r.assigned_at) for r in roles]
