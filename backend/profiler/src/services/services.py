from abc import ABC, abstractmethod
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.repository import ProfileData, ProfileLookupData, RoleData


class ProfileNotFoundError(Exception):
    pass


class EmailAlreadyConfirmedError(Exception):
    pass


class InvalidConfirmationTokenError(Exception):
    pass


class ExpiredConfirmationTokenError(Exception):
    pass


class ProfileService(ABC):
    @abstractmethod
    async def create_profile(
        self, session: AsyncSession, user_id: str, name: str, email: str
    ) -> None:
        pass

    @abstractmethod
    async def get_profile(
        self, session: AsyncSession, user_id: str
    ) -> ProfileData:
        pass

    @abstractmethod
    async def update_profile(
        self,
        session: AsyncSession,
        user_id: str,
        name: Optional[str] = None,
        city: Optional[str] = None,
    ) -> ProfileData:
        pass

    @abstractmethod
    async def delete_profile(self, session: AsyncSession, user_id: str) -> None:
        pass

    @abstractmethod
    async def find_profiles_by_email(
        self, session: AsyncSession, email: str
    ) -> list[ProfileLookupData]:
        pass

    @abstractmethod
    async def list_profiles(
        self, session: AsyncSession, limit: int = 20, offset: int = 0
    ) -> list[ProfileData]:
        pass


class RolesService(ABC):
    @abstractmethod
    async def get_roles(self, session: AsyncSession, user_id: str) -> list[RoleData]:
        pass


class EmailConfirmationService(ABC):
    @abstractmethod
    async def create_email_confirmation_token(
        self, session: AsyncSession, user_id: str
    ) -> str:
        pass

    @abstractmethod
    async def confirm_email(self, session: AsyncSession, token: str) -> None:
        pass
