import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class RoleData:
    role: str
    assigned_at: Optional[datetime.datetime] = None


@dataclass
class ProfileData:
    user_id: str
    name: str
    email: str
    city: Optional[str] = None
    avatar_url: Optional[str] = None
    email_confirmed: bool = False
    roles: list[RoleData] = field(default_factory=list)
    created_at: Optional[datetime.datetime] = None


@dataclass
class ProfileLookupData:
    user_id: str
    name: str
    avatar_url: Optional[str] = None


@dataclass
class EmailConfirmationTokenData:
    token: str
    user_id: str
    expires_at: datetime.datetime


class ProfileRepository(ABC):
    @abstractmethod
    async def create_profile(
        self, session: AsyncSession, user_id: str, name: str, email: str
    ) -> None:
        pass

    @abstractmethod
    async def get_profile(
        self, session: AsyncSession, user_id: str
    ) -> Optional[ProfileData]:
        pass

    @abstractmethod
    async def update_profile(
        self,
        session: AsyncSession,
        user_id: str,
        name: Optional[str] = None,
        city: Optional[str] = None,
    ) -> None:
        pass

    @abstractmethod
    async def delete_profile(self, session: AsyncSession, user_id: str) -> bool:
        pass

    @abstractmethod
    async def find_profiles_by_email(
        self, session: AsyncSession, email: str
    ) -> list[ProfileLookupData]:
        pass

    @abstractmethod
    async def get_roles(self, session: AsyncSession, user_id: str) -> list[RoleData]:
        pass

    @abstractmethod
    async def create_email_confirmation_token(
        self, session: AsyncSession, token_data: EmailConfirmationTokenData
    ) -> None:
        pass

    @abstractmethod
    async def get_email_confirmation_token(
        self, session: AsyncSession, token: str
    ) -> Optional[EmailConfirmationTokenData]:
        pass

    @abstractmethod
    async def confirm_email(
        self, session: AsyncSession, user_id: str
    ) -> None:
        pass

    @abstractmethod
    async def is_email_confirmed(
        self, session: AsyncSession, email: str
    ) -> bool:
        pass

    @abstractmethod
    async def list_profiles(
        self, session: AsyncSession, limit: int = 20, offset: int = 0
    ) -> list[ProfileData]:
        pass
