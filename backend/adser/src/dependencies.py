from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.service import AdsService
from src.clients.profiler_client import ProfilerClient
from src.clients.s3_client import S3Client
from src.services.external_data_service import ExternalCityService


def get_ads_service(request: Request) -> AdsService:
    return request.app.state.ads_service


def get_profiler_client(request: Request) -> ProfilerClient:
    return request.app.state.profiler_client


def get_s3_client(request: Request) -> S3Client:
    return request.app.state.s3_client


def get_external_city_service(request: Request) -> ExternalCityService:
    return request.app.state.external_city_service


async def get_session(request: Request) -> AsyncSession:
    async with request.app.state.session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
