from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.repository import ProfileRepository, RoleData
from src.services.services import RolesService, ProfileNotFoundError, InvalidRoleError


class RolesServiceImpl(RolesService):
    def __init__(self, repository: ProfileRepository):
        self.repository = repository

    async def get_roles(self, session: AsyncSession, user_id: str) -> list[RoleData]:
        return await self.repository.get_roles(session, user_id)

    async def assign_role(self, session: AsyncSession, user_id: str, role: str) -> list[RoleData]:
        normalized = role.upper()
        if normalized not in {"MODERATOR", "ADMIN"}:
            raise InvalidRoleError("Unsupported role")
        try:
            await self.repository.assign_role(session, user_id, normalized)
        except ValueError:
            raise ProfileNotFoundError(f"Profile {user_id} not found")
        await session.commit()
        return await self.repository.get_roles(session, user_id)

    async def remove_role(self, session: AsyncSession, user_id: str, role: str) -> list[RoleData]:
        normalized = role.upper()
        if normalized not in {"MODERATOR", "ADMIN"}:
            raise InvalidRoleError("Unsupported role")
        removed = await self.repository.remove_role(session, user_id, normalized)
        if not removed:
            profile = await self.repository.get_profile(session, user_id)
            if profile is None:
                raise ProfileNotFoundError(f"Profile {user_id} not found")
        await session.commit()
        return await self.repository.get_roles(session, user_id)
