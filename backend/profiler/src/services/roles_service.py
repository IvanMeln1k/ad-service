from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.repository import ProfileRepository, RoleData
from src.services.services import RolesService


class RolesServiceImpl(RolesService):
    def __init__(self, repository: ProfileRepository):
        self.repository = repository

    async def get_roles(self, session: AsyncSession, user_id: str) -> list[RoleData]:
        return await self.repository.get_roles(session, user_id)
