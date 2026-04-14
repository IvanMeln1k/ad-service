from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

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
