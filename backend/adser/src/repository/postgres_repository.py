import datetime
from typing import Optional

from sqlalchemy import select, update, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import func as sa_func

from src.models.models import Ad, AdPhoto, AdBan, AdStatus, AdCategory
from src.repository.repository import AdsRepository, AdData, PhotoData, BanData


class PostgresAdsRepository(AdsRepository):

    def _ad_to_data(self, ad: Ad, photos: list[AdPhoto] = None, is_banned: bool = False, ban_reason: Optional[str] = None) -> AdData:
        return AdData(
            id=str(ad.id),
            user_id=ad.user_id,
            title=ad.title,
            description=ad.description,
            status=ad.status.value,
            price=float(ad.price) if ad.price is not None else None,
            city=ad.city,
            category=ad.category.value if ad.category else None,
            photos=[
                PhotoData(id=str(p.id), ad_id=str(p.ad_id), s3_key=p.s3_key, position=p.position, uploaded_at=p.uploaded_at)
                for p in (photos or [])
            ],
            is_banned=is_banned,
            ban_reason=ban_reason,
            created_at=ad.created_at,
            updated_at=ad.updated_at,
            deleted_at=ad.deleted_at,
        )

    async def create_ad(self, session: AsyncSession, user_id: str, title: str, description: str,
                        price: Optional[float] = None, city: Optional[str] = None, category: Optional[str] = None) -> AdData:
        ad = Ad(
            user_id=user_id, title=title, description=description,
            price=price, city=city,
            category=AdCategory(category) if category else None,
        )
        session.add(ad)
        await session.flush()
        return self._ad_to_data(ad)

    async def get_ad(self, session: AsyncSession, ad_id: str) -> Optional[AdData]:
        stmt = select(Ad).where(and_(Ad.id == ad_id, Ad.deleted_at.is_(None)))
        result = await session.execute(stmt)
        ad = result.scalar_one_or_none()
        if not ad:
            return None

        photos_stmt = select(AdPhoto).where(AdPhoto.ad_id == ad_id).order_by(AdPhoto.position)
        photos = (await session.execute(photos_stmt)).scalars().all()

        active_ban = await self.get_active_ban(session, ad_id)
        return self._ad_to_data(ad, photos, active_ban is not None, active_ban.reason if active_ban else None)

    async def list_ads(self, session: AsyncSession, limit: int, offset: int, search: Optional[str] = None,
                       include_banned: bool = False, category: Optional[str] = None, city: Optional[str] = None,
                       price_min: Optional[float] = None, price_max: Optional[float] = None,
                       sort_by: str = "created_at", sort_order: str = "desc") -> tuple[list[AdData], int]:
        conditions = [Ad.deleted_at.is_(None), Ad.status == AdStatus.ACTIVE]
        if search:
            conditions.append(or_(Ad.title.ilike(f"%{search}%"), Ad.description.ilike(f"%{search}%")))
        if category:
            conditions.append(Ad.category == AdCategory(category))
        if city:
            conditions.append(Ad.city.ilike(f"%{city}%"))
        if price_min is not None:
            conditions.append(Ad.price >= price_min)
        if price_max is not None:
            conditions.append(Ad.price <= price_max)

        where_clause = and_(*conditions)

        count_stmt = select(sa_func.count()).select_from(Ad).where(where_clause)
        total = (await session.execute(count_stmt)).scalar() or 0

        sort_column = {"created_at": Ad.created_at, "price": Ad.price, "title": Ad.title}.get(sort_by, Ad.created_at)
        order = sort_column.asc() if sort_order == "asc" else sort_column.desc()

        stmt = select(Ad).where(where_clause).order_by(order).limit(limit).offset(offset)
        result = await session.execute(stmt)
        ads = result.scalars().all()

        data = []
        for ad in ads:
            active_ban = await self.get_active_ban(session, str(ad.id))
            if active_ban and not include_banned:
                continue
            photos_stmt = select(AdPhoto).where(AdPhoto.ad_id == ad.id).order_by(AdPhoto.position)
            photos = (await session.execute(photos_stmt)).scalars().all()
            data.append(self._ad_to_data(ad, photos, active_ban is not None, active_ban.reason if active_ban else None))
        return data, total

    async def list_user_ads(self, session: AsyncSession, user_id: str, limit: int, offset: int) -> list[AdData]:
        stmt = (
            select(Ad)
            .where(and_(Ad.user_id == user_id, Ad.deleted_at.is_(None)))
            .order_by(Ad.created_at.desc())
            .limit(limit).offset(offset)
        )
        result = await session.execute(stmt)
        ads = result.scalars().all()

        data = []
        for ad in ads:
            photos_stmt = select(AdPhoto).where(AdPhoto.ad_id == ad.id).order_by(AdPhoto.position)
            photos = (await session.execute(photos_stmt)).scalars().all()
            active_ban = await self.get_active_ban(session, str(ad.id))
            data.append(self._ad_to_data(ad, photos, active_ban is not None, active_ban.reason if active_ban else None))
        return data

    async def update_ad(
        self,
        session: AsyncSession,
        ad_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[float] = None,
        city: Optional[str] = None,
        category: Optional[str] = None,
    ) -> None:
        values = {}
        if title is not None:
            values["title"] = title
        if description is not None:
            values["description"] = description
        if price is not None:
            values["price"] = price
        if city is not None:
            values["city"] = city
        if category is not None:
            values["category"] = AdCategory(category)
        if not values:
            return
        values["updated_at"] = datetime.datetime.utcnow()
        stmt = update(Ad).where(Ad.id == ad_id).values(**values)
        await session.execute(stmt)
        await session.flush()

    async def set_ad_status(self, session: AsyncSession, ad_id: str, status: str) -> None:
        stmt = (
            update(Ad)
            .where(Ad.id == ad_id)
            .values(status=AdStatus(status), updated_at=datetime.datetime.utcnow())
        )
        await session.execute(stmt)
        await session.flush()

    async def soft_delete_ad(self, session: AsyncSession, ad_id: str) -> bool:
        stmt = (
            update(Ad)
            .where(and_(Ad.id == ad_id, Ad.deleted_at.is_(None)))
            .values(deleted_at=datetime.datetime.utcnow())
        )
        result = await session.execute(stmt)
        await session.flush()
        return (result.rowcount or 0) > 0

    async def add_photo(self, session: AsyncSession, ad_id: str, s3_key: str, position: int) -> PhotoData:
        photo = AdPhoto(ad_id=ad_id, s3_key=s3_key, position=position)
        session.add(photo)
        await session.flush()
        return PhotoData(id=str(photo.id), ad_id=str(photo.ad_id), s3_key=photo.s3_key, position=photo.position, uploaded_at=photo.uploaded_at)

    async def delete_photo(self, session: AsyncSession, photo_id: str) -> bool:
        from sqlalchemy import delete
        stmt = delete(AdPhoto).where(AdPhoto.id == photo_id)
        result = await session.execute(stmt)
        return (result.rowcount or 0) > 0

    async def create_ban(self, session: AsyncSession, ad_id: str, moderator_id: str, reason: str) -> BanData:
        ban = AdBan(ad_id=ad_id, moderator_id=moderator_id, reason=reason)
        session.add(ban)
        await session.flush()
        return BanData(id=str(ban.id), ad_id=str(ban.ad_id), moderator_id=ban.moderator_id, reason=ban.reason, banned_at=ban.banned_at)

    async def unban(self, session: AsyncSession, ad_id: str, unbanned_by_id: str, unban_reason: str) -> bool:
        stmt = (
            update(AdBan)
            .where(and_(AdBan.ad_id == ad_id, AdBan.unbanned_at.is_(None)))
            .values(unbanned_by_id=unbanned_by_id, unban_reason=unban_reason, unbanned_at=datetime.datetime.utcnow())
        )
        result = await session.execute(stmt)
        await session.flush()
        return (result.rowcount or 0) > 0

    async def get_bans(self, session: AsyncSession, ad_id: str) -> list[BanData]:
        stmt = select(AdBan).where(AdBan.ad_id == ad_id).order_by(AdBan.banned_at.desc())
        result = await session.execute(stmt)
        return [
            BanData(
                id=str(b.id), ad_id=str(b.ad_id), moderator_id=b.moderator_id, reason=b.reason,
                banned_at=b.banned_at, unbanned_by_id=b.unbanned_by_id, unban_reason=b.unban_reason, unbanned_at=b.unbanned_at,
            )
            for b in result.scalars().all()
        ]

    async def get_active_ban(self, session: AsyncSession, ad_id: str) -> Optional[AdBan]:
        stmt = select(AdBan).where(and_(AdBan.ad_id == ad_id, AdBan.unbanned_at.is_(None)))
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def has_active_ban(self, session: AsyncSession, ad_id: str) -> bool:
        return await self.get_active_ban(session, ad_id) is not None
