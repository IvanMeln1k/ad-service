from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.config import config
from src.events.publisher import EventPublisher
from src.repository.repository import AdsRepository, AdData, PhotoData, BanData
from src.services.service import (
    AdsService,
    AdNotFoundError,
    NotOwnerError,
    AdBannedError,
    AdAlreadyClosedError,
    AdNotClosedError,
)


class AdsServiceImpl(AdsService):
    def __init__(self, repository: AdsRepository, publisher: EventPublisher):
        self.repository = repository
        self.publisher = publisher

    async def _get_or_404(self, session: AsyncSession, ad_id: str) -> AdData:
        ad = await self.repository.get_ad(session, ad_id)
        if not ad:
            raise AdNotFoundError(f"Ad {ad_id} not found")
        return ad

    async def _check_owner(self, ad: AdData, user_id: str) -> None:
        if ad.user_id != user_id:
            raise NotOwnerError("Not the owner of this ad")

    async def _publish_event(self, event: str, ad_id: str) -> None:
        await self.publisher.publish(
            topic=config.KAFKA_TOPIC_ADS,
            key=ad_id,
            value={"event": event, "ad_id": ad_id},
        )

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
        ad = await self.repository.create_ad(session, user_id, title, description, price, city, category)
        await session.commit()
        await self._publish_event("ad.created", ad.id)
        return ad

    async def get_ad(self, session: AsyncSession, ad_id: str) -> AdData:
        return await self._get_or_404(session, ad_id)

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
        return await self.repository.list_ads(
            session,
            limit,
            offset,
            search,
            include_banned,
            category,
            city,
            price_min,
            price_max,
            sort_by,
            sort_order,
        )

    async def list_user_ads(self, session: AsyncSession, user_id: str, limit: int, offset: int) -> list[AdData]:
        return await self.repository.list_user_ads(session, user_id, limit, offset)

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
        ad = await self._get_or_404(session, ad_id)
        await self._check_owner(ad, user_id)
        await self.repository.update_ad(
            session,
            ad_id,
            title=title,
            description=description,
            price=price,
            city=city,
            category=category,
        )
        await session.commit()
        await self._publish_event("ad.updated", ad_id)
        return await self._get_or_404(session, ad_id)

    async def delete_ad(self, session: AsyncSession, ad_id: str, user_id: str) -> None:
        ad = await self._get_or_404(session, ad_id)
        await self._check_owner(ad, user_id)
        if ad.is_banned:
            raise AdBannedError("Cannot delete a banned ad")
        deleted = await self.repository.soft_delete_ad(session, ad_id)
        if not deleted:
            raise AdNotFoundError(f"Ad {ad_id} not found")
        await session.commit()
        await self._publish_event("ad.deleted", ad_id)

    async def close_ad(self, session: AsyncSession, ad_id: str, user_id: str) -> None:
        ad = await self._get_or_404(session, ad_id)
        await self._check_owner(ad, user_id)
        if ad.is_banned:
            raise AdBannedError("Cannot close a banned ad")
        if ad.status == "CLOSED":
            raise AdAlreadyClosedError("Ad is already closed")
        await self.repository.set_ad_status(session, ad_id, "CLOSED")
        await session.commit()
        await self._publish_event("ad.closed", ad_id)

    async def reopen_ad(self, session: AsyncSession, ad_id: str, user_id: str) -> None:
        ad = await self._get_or_404(session, ad_id)
        await self._check_owner(ad, user_id)
        if ad.status != "CLOSED":
            raise AdNotClosedError("Ad is not closed")
        if ad.is_banned:
            raise AdBannedError("Cannot reopen a banned ad")
        await self.repository.set_ad_status(session, ad_id, "ACTIVE")
        await session.commit()
        await self._publish_event("ad.reopened", ad_id)

    async def add_photo(self, session: AsyncSession, ad_id: str, user_id: str, s3_key: str, position: int) -> PhotoData:
        ad = await self._get_or_404(session, ad_id)
        await self._check_owner(ad, user_id)
        photo = await self.repository.add_photo(session, ad_id, s3_key, position)
        await session.commit()
        return photo

    async def delete_photo(self, session: AsyncSession, ad_id: str, user_id: str, photo_id: str) -> None:
        ad = await self._get_or_404(session, ad_id)
        await self._check_owner(ad, user_id)
        deleted = await self.repository.delete_photo(session, photo_id)
        if not deleted:
            raise AdNotFoundError(f"Photo {photo_id} not found")
        await session.commit()

    async def ban_ad(self, session: AsyncSession, ad_id: str, moderator_id: str, reason: str) -> BanData:
        await self._get_or_404(session, ad_id)
        ban = await self.repository.create_ban(session, ad_id, moderator_id, reason)
        await session.commit()
        await self._publish_event("ad.banned", ad_id)
        return ban

    async def unban_ad(self, session: AsyncSession, ad_id: str, moderator_id: str, unban_reason: str) -> None:
        await self._get_or_404(session, ad_id)
        unbanned = await self.repository.unban(session, ad_id, moderator_id, unban_reason)
        if not unbanned:
            raise AdNotFoundError("No active ban found")
        await session.commit()
        await self._publish_event("ad.unbanned", ad_id)

    async def get_bans(self, session: AsyncSession, ad_id: str) -> list[BanData]:
        await self._get_or_404(session, ad_id)
        return await self.repository.get_bans(session, ad_id)
