import datetime
import uuid

import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from src.auth import AuthProvider, AuthUser
from src.clients.s3_client import S3Client
from src.clients.profiler_client import ProfilerClient, ProfileInfo
from src.events.publisher import EventPublisher
from src.repository.repository import AdsRepository, AdData, PhotoData, BanData
from src.services.ads_service import AdsServiceImpl
from src.services.external_data_service import ExternalCityService, CityContext
from src.routers import (
    list_ads, my_ads, get_ad, create_ad, update_ad, delete_ad,
    close_ad, reopen_ad, confirm_photo, delete_photo,
    presign_photo,
    ban_ad, unban_ad, get_bans, attributes, city_context, seo,
)


class FakeEventPublisher(EventPublisher):
    def __init__(self):
        self.events: list[dict] = []

    async def publish(self, topic, key, value):
        self.events.append({"topic": topic, "key": key, "value": value})

    async def start(self):
        pass

    async def stop(self):
        pass


class FakeAuthProvider(AuthProvider):
    def __init__(self):
        self.user = AuthUser(user_id="user-1", roles=[], email_confirmed=True)

    async def authenticate(self, token: str) -> AuthUser:
        return self.user


class FakeAdsRepository(AdsRepository):
    def __init__(self):
        self.ads: dict[str, AdData] = {}
        self.photos: dict[str, PhotoData] = {}
        self.bans: dict[str, list[BanData]] = {}

    async def create_ad(self, session, user_id, title, description, price=None, city=None, category=None):
        ad_id = str(uuid.uuid4())
        ad = AdData(
            id=ad_id, user_id=user_id, title=title, description=description,
            price=price, city=city, category=category,
            status="ACTIVE", created_at=datetime.datetime(2026, 1, 1),
            updated_at=datetime.datetime(2026, 1, 1),
        )
        self.ads[ad_id] = ad
        return ad

    async def get_ad(self, session, ad_id):
        ad = self.ads.get(ad_id)
        if ad and ad.deleted_at is None:
            ad.photos = [p for p in self.photos.values() if p.ad_id == ad_id]
            ad.is_banned = await self.has_active_ban(session, ad_id)
            return ad
        return None

    async def list_ads(
        self,
        session,
        limit,
        offset,
        search=None,
        include_banned=False,
        category=None,
        city=None,
        price_min=None,
        price_max=None,
        sort_by="created_at",
        sort_order="desc",
    ):
        ads = [a for a in self.ads.values() if a.deleted_at is None and a.status == "ACTIVE"]
        if search:
            ads = [a for a in ads if search.lower() in a.title.lower() or search.lower() in a.description.lower()]
        if category:
            ads = [a for a in ads if a.category == category]
        if city:
            ads = [a for a in ads if a.city and city.lower() in a.city.lower()]
        if price_min is not None:
            ads = [a for a in ads if a.price is not None and a.price >= price_min]
        if price_max is not None:
            ads = [a for a in ads if a.price is not None and a.price <= price_max]
        if sort_by == "price":
            ads.sort(key=lambda a: a.price if a.price is not None else 0, reverse=sort_order == "desc")
        elif sort_by == "title":
            ads.sort(key=lambda a: a.title.lower(), reverse=sort_order == "desc")
        total = len(ads)
        return ads[offset:offset + limit], total

    async def list_user_ads(self, session, user_id, limit, offset):
        ads = [a for a in self.ads.values() if a.user_id == user_id and a.deleted_at is None]
        return ads[offset:offset + limit]

    async def update_ad(self, session, ad_id, title=None, description=None, price=None, city=None, category=None):
        if ad_id in self.ads:
            if title is not None:
                self.ads[ad_id].title = title
            if description is not None:
                self.ads[ad_id].description = description
            if price is not None:
                self.ads[ad_id].price = price
            if city is not None:
                self.ads[ad_id].city = city
            if category is not None:
                self.ads[ad_id].category = category

    async def set_ad_status(self, session, ad_id, status):
        if ad_id in self.ads:
            self.ads[ad_id].status = status

    async def soft_delete_ad(self, session, ad_id):
        if ad_id in self.ads and self.ads[ad_id].deleted_at is None:
            self.ads[ad_id].deleted_at = datetime.datetime.utcnow()
            return True
        return False

    async def add_photo(self, session, ad_id, s3_key, position):
        photo_id = str(uuid.uuid4())
        photo = PhotoData(id=photo_id, ad_id=ad_id, s3_key=s3_key, position=position)
        self.photos[photo_id] = photo
        return photo

    async def delete_photo(self, session, photo_id):
        if photo_id in self.photos:
            del self.photos[photo_id]
            return True
        return False

    async def create_ban(self, session, ad_id, moderator_id, reason):
        ban_id = str(uuid.uuid4())
        ban = BanData(id=ban_id, ad_id=ad_id, moderator_id=moderator_id, reason=reason, banned_at=datetime.datetime.utcnow())
        self.bans.setdefault(ad_id, []).append(ban)
        return ban

    async def unban(self, session, ad_id, unbanned_by_id, unban_reason):
        for ban in self.bans.get(ad_id, []):
            if ban.unbanned_at is None:
                ban.unbanned_by_id = unbanned_by_id
                ban.unban_reason = unban_reason
                ban.unbanned_at = datetime.datetime.utcnow()
                return True
        return False

    async def get_bans(self, session, ad_id):
        return self.bans.get(ad_id, [])

    async def has_active_ban(self, session, ad_id):
        return any(b.unbanned_at is None for b in self.bans.get(ad_id, []))


class FakeSession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def close(self):
        pass

    async def commit(self):
        pass

    async def flush(self):
        pass


class FakeSessionFactory:
    def __call__(self):
        return FakeSession()


@pytest.fixture
def fake_repo():
    return FakeAdsRepository()


@pytest.fixture
def fake_publisher():
    return FakeEventPublisher()


class FakeS3Client(S3Client):
    def generate_presigned_put(self, key: str, content_type: str, expires_in: int = 600) -> str:
        return f"https://fake-s3.local/{key}?content_type={content_type}&expires={expires_in}"


class FakeProfilerClient(ProfilerClient):
    async def get_profile(self, user_id):
        return ProfileInfo(
            user_id=user_id,
            name="Test User",
            email="test@example.com",
            city="Moscow",
            avatar_url=None,
        )


class FakeExternalCityService(ExternalCityService):
    async def get_city_context(self, city: str) -> CityContext:
        if city.lower() == "moscow":
            return CityContext(
                city="Moscow",
                country="RU",
                temperature_c=16.5,
                weather_description="облачно",
                source="openweather",
                available=True,
            )
        return CityContext(
            city=city,
            country=None,
            temperature_c=None,
            weather_description=None,
            source="openweather",
            available=False,
            unavailable_reason="city_not_found",
        )


@pytest.fixture
def fake_auth():
    return FakeAuthProvider()


@pytest.fixture
def fake_profiler():
    return FakeProfilerClient()


@pytest.fixture
def fake_s3():
    return FakeS3Client()


@pytest.fixture
def fake_external_city_service():
    return FakeExternalCityService()


@pytest.fixture
def app(fake_repo, fake_publisher, fake_auth, fake_profiler, fake_s3, fake_external_city_service):
    test_app = FastAPI()
    test_app.state.ads_service = AdsServiceImpl(repository=fake_repo, publisher=fake_publisher)
    test_app.state.auth_provider = fake_auth
    test_app.state.profiler_client = fake_profiler
    test_app.state.s3_client = fake_s3
    test_app.state.external_city_service = fake_external_city_service
    test_app.state.session_factory = FakeSessionFactory()

    test_app.include_router(attributes.router)
    test_app.include_router(list_ads.router)
    test_app.include_router(my_ads.router)
    test_app.include_router(create_ad.router)
    test_app.include_router(get_ad.router)
    test_app.include_router(update_ad.router)
    test_app.include_router(delete_ad.router)
    test_app.include_router(close_ad.router)
    test_app.include_router(reopen_ad.router)
    test_app.include_router(confirm_photo.router)
    test_app.include_router(delete_photo.router)
    test_app.include_router(presign_photo.router)
    test_app.include_router(ban_ad.router)
    test_app.include_router(unban_ad.router)
    test_app.include_router(get_bans.router)
    test_app.include_router(city_context.router)
    test_app.include_router(seo.router)
    return test_app


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


AUTH_HEADERS = {"Authorization": "Bearer test-token"}
