from abc import ABC, abstractmethod
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.repository import AdData, PhotoData, BanData


class AdNotFoundError(Exception):
    pass


class NotOwnerError(Exception):
    pass


class AdBannedError(Exception):
    pass


class AdAlreadyClosedError(Exception):
    pass


class AdNotClosedError(Exception):
    pass


class AdsService(ABC):
    @abstractmethod
    async def create_ad(
        self,
        session: AsyncSession,
        user_id: str,
        title: str,
        description: str,
        price: Optional[float] = None,
        city: Optional[str] = None,
        category: Optional[str] = None,
    ) -> AdData:
        pass

    @abstractmethod
    async def get_ad(self, session: AsyncSession, ad_id: str) -> AdData:
        pass

    @abstractmethod
    async def list_ads(
        self,
        session: AsyncSession,
        limit: int,
        offset: int,
        search: Optional[str] = None,
        include_banned: bool = False,
        category: Optional[str] = None,
        city: Optional[str] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[AdData], int]:
        pass

    @abstractmethod
    async def list_user_ads(self, session: AsyncSession, user_id: str, limit: int, offset: int) -> list[AdData]:
        pass

    @abstractmethod
    async def update_ad(
        self,
        session: AsyncSession,
        ad_id: str,
        user_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[float] = None,
        city: Optional[str] = None,
        category: Optional[str] = None,
    ) -> AdData:
        pass

    @abstractmethod
    async def delete_ad(self, session: AsyncSession, ad_id: str, user_id: str) -> None:
        pass

    @abstractmethod
    async def close_ad(self, session: AsyncSession, ad_id: str, user_id: str) -> None:
        pass

    @abstractmethod
    async def reopen_ad(self, session: AsyncSession, ad_id: str, user_id: str) -> None:
        pass

    @abstractmethod
    async def add_photo(self, session: AsyncSession, ad_id: str, user_id: str, s3_key: str, position: int) -> PhotoData:
        pass

    @abstractmethod
    async def delete_photo(self, session: AsyncSession, ad_id: str, user_id: str, photo_id: str) -> None:
        pass

    @abstractmethod
    async def ban_ad(self, session: AsyncSession, ad_id: str, moderator_id: str, reason: str) -> BanData:
        pass

    @abstractmethod
    async def unban_ad(self, session: AsyncSession, ad_id: str, moderator_id: str, unban_reason: str) -> None:
        pass

    @abstractmethod
    async def get_bans(self, session: AsyncSession, ad_id: str) -> list[BanData]:
        pass
