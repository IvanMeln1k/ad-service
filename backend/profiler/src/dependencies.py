from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import AuthUser, get_current_user
from src.services.services import ProfileService, RolesService, EmailConfirmationService


def get_profile_service(request: Request) -> ProfileService:
    return request.app.state.profile_service


def get_roles_service(request: Request) -> RolesService:
    return request.app.state.roles_service


def get_email_service(request: Request) -> EmailConfirmationService:
    return request.app.state.email_service


async def get_session(request: Request) -> AsyncSession:
    async with request.app.state.session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_user_roles(
    user: AuthUser = Depends(get_current_user),
    roles_service: RolesService = Depends(get_roles_service),
    session: AsyncSession = Depends(get_session),
) -> set[str]:
    roles = await roles_service.get_roles(session, user.user_id)
    return {r.role for r in roles}


async def require_admin(
    roles: set[str] = Depends(get_current_user_roles),
) -> set[str]:
    if "ADMIN" not in roles:
        raise HTTPException(status_code=403, detail="Admin role required")
    return roles


async def require_staff(
    roles: set[str] = Depends(get_current_user_roles),
) -> set[str]:
    if "ADMIN" not in roles and "MODERATOR" not in roles:
        raise HTTPException(status_code=403, detail="Moderator role required")
    return roles
