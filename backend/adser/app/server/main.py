from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.config import config
from src.auth import HttpAuthProvider
from src.clients.profiler_client import HttpProfilerClient
from src.clients.s3_client import MinioS3Client
from src.events.kafka_publisher import KafkaEventPublisher
from src.repository.postgres_repository import PostgresAdsRepository
from src.services.ads_service import AdsServiceImpl
from src.services.external_data_service import OpenWeatherCityService
from src.routers import (
    list_ads, my_ads, get_ad, create_ad, update_ad, delete_ad,
    close_ad, reopen_ad,
    presign_photo, confirm_photo, delete_photo,
    ban_ad, unban_ad, get_bans,
    attributes,
)
from src.routers import city_context, seo

publisher = KafkaEventPublisher(bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await publisher.start()
    yield
    await publisher.stop()


app = FastAPI(title="Adser Service", version="1.0.0", lifespan=lifespan)

engine = create_async_engine(config.database_url)
app.state.session_factory = async_sessionmaker(engine, expire_on_commit=False)

repository = PostgresAdsRepository()
app.state.ads_service = AdsServiceImpl(repository=repository, publisher=publisher)
app.state.auth_provider = HttpAuthProvider(auther_url=config.AUTHER_URL, profiler_url=config.PROFILER_URL)
app.state.profiler_client = HttpProfilerClient(base_url=config.PROFILER_URL)
app.state.s3_client = MinioS3Client(
    endpoint=config.S3_ENDPOINT,
    public_endpoint=config.S3_PUBLIC_ENDPOINT,
    access_key=config.S3_ACCESS_KEY,
    secret_key=config.S3_SECRET_KEY,
    bucket=config.S3_BUCKET,
)
app.state.external_city_service = OpenWeatherCityService(
    base_url=config.OPENWEATHER_API_BASE_URL,
    api_key=config.OPENWEATHER_API_KEY,
    timeout_s=config.EXTERNAL_API_TIMEOUT_S,
    retries=config.EXTERNAL_API_RETRIES,
    rate_limit=config.EXTERNAL_API_RATE_LIMIT,
    rate_window_s=config.EXTERNAL_API_RATE_WINDOW_S,
)

# Static paths first, then parameterized
app.include_router(attributes.router)
app.include_router(list_ads.router)
app.include_router(my_ads.router)
app.include_router(create_ad.router)
app.include_router(get_ad.router)
app.include_router(update_ad.router)
app.include_router(delete_ad.router)
app.include_router(close_ad.router)
app.include_router(reopen_ad.router)
app.include_router(presign_photo.router)
app.include_router(confirm_photo.router)
app.include_router(delete_photo.router)
app.include_router(ban_ad.router)
app.include_router(unban_ad.router)
app.include_router(get_bans.router)
app.include_router(city_context.router)
app.include_router(seo.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
