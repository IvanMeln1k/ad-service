from fastapi import APIRouter, Depends, Query

from src.dependencies import get_external_city_service
from src.schemas.schemas import CityContextResponse
from src.services.external_data_service import ExternalCityService, ExternalDataUnavailableError

router = APIRouter()


@router.get("/api/v1/external/city-context", response_model=CityContextResponse)
async def get_city_context(
    city: str = Query(..., min_length=2, max_length=100),
    service: ExternalCityService = Depends(get_external_city_service),
):
    try:
        city_context = await service.get_city_context(city)
        return CityContextResponse(
            city=city_context.city,
            country=city_context.country,
            temperature_c=city_context.temperature_c,
            weather_description=city_context.weather_description,
            source=city_context.source,
            available=city_context.available,
            unavailable_reason=city_context.unavailable_reason,
        )
    except ExternalDataUnavailableError as exc:
        return CityContextResponse(
            city=city,
            country=None,
            temperature_c=None,
            weather_description=None,
            source="openweather",
            available=False,
            unavailable_reason=exc.reason,
        )
