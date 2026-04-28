import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class PhotoData:
    id: str
    ad_id: str
    s3_key: str
    position: int
    uploaded_at: Optional[datetime.datetime] = None


@dataclass
class BanData:
    id: str
    ad_id: str
    moderator_id: str
    reason: str
    banned_at: Optional[datetime.datetime] = None
    unbanned_by_id: Optional[str] = None
    unban_reason: Optional[str] = None
    unbanned_at: Optional[datetime.datetime] = None


@dataclass
class AdData:
    id: str
    user_id: str
    title: str
    description: str
    status: str
    price: Optional[float] = None
    city: Optional[str] = None
    category: Optional[str] = None
    photos: list[PhotoData] = field(default_factory=list)
    is_banned: bool = False
    ban_reason: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    deleted_at: Optional[datetime.datetime] = None


class AdsRepository(ABC):
    @abstractmethod
    async def create_ad(self, session: AsyncSession, user_id: str, title: str, description: str,
                        price: Optional[float] = None, city: Optional[str] = None, category: Optional[str] = None) -> AdData:
        pass

    @abstractmethod
    async def get_ad(self, session: AsyncSession, ad_id: str) -> Optional[AdData]:
        pass

    @abstractmethod
    async def list_ads(self, session: AsyncSession, limit: int, offset: int, search: Optional[str] = None,
                       include_banned: bool = False, category: Optional[str] = None, city: Optional[str] = None,
                       price_min: Optional[float] = None, price_max: Optional[float] = None,
                       sort_by: str = "created_at", sort_order: str = "desc") -> tuple[list[AdData], int]:
        pass

    @abstractmethod
    async def list_user_ads(self, session: AsyncSession, user_id: str, limit: int, offset: int) -> list[AdData]:
        pass

    @abstractmethod
    async def update_ad(self, session: AsyncSession, ad_id: str, title: Optional[str] = None,
                        description: Optional[str] = None, price: Optional[float] = None,
                        city: Optional[str] = None, category: Optional[str] = None) -> None:
        pass

    @abstractmethod
    async def set_ad_status(self, session: AsyncSession, ad_id: str, status: str) -> None:
        pass

    @abstractmethod
    async def soft_delete_ad(self, session: AsyncSession, ad_id: str) -> bool:
        pass

    @abstractmethod
    async def add_photo(self, session: AsyncSession, ad_id: str, s3_key: str, position: int) -> PhotoData:
        pass

    @abstractmethod
    async def delete_photo(self, session: AsyncSession, photo_id: str) -> bool:
        pass

    @abstractmethod
    async def create_ban(self, session: AsyncSession, ad_id: str, moderator_id: str, reason: str) -> BanData:
        pass

    @abstractmethod
    async def unban(self, session: AsyncSession, ad_id: str, unbanned_by_id: str, unban_reason: str) -> bool:
        pass

    @abstractmethod
    async def get_bans(self, session: AsyncSession, ad_id: str) -> list[BanData]:
        pass

    @abstractmethod
    async def has_active_ban(self, session: AsyncSession, ad_id: str) -> bool:
        pass
