import asyncio
import time
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass
from typing import Optional

import httpx


@dataclass
class CityContext:
    city: str
    country: Optional[str]
    temperature_c: Optional[float]
    weather_description: Optional[str]
    source: str
    available: bool
    unavailable_reason: Optional[str] = None


class ExternalDataUnavailableError(Exception):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


class ExternalCityService(ABC):
    @abstractmethod
    async def get_city_context(self, city: str) -> CityContext:
        pass


class OpenWeatherCityService(ExternalCityService):
    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout_s: float = 2.5,
        retries: int = 2,
        rate_limit: int = 30,
        rate_window_s: int = 60,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_s = timeout_s
        self.retries = retries
        self.rate_limit = rate_limit
        self.rate_window_s = rate_window_s
        self._calls: deque[float] = deque()
        self._lock = asyncio.Lock()
        self._open_meteo_weather_codes = {
            0: "ясно",
            1: "преимущественно ясно",
            2: "переменная облачность",
            3: "пасмурно",
            45: "туман",
            48: "изморозь",
            51: "морось",
            53: "морось",
            55: "сильная морось",
            56: "переохлажденная морось",
            57: "сильная переохлажденная морось",
            61: "небольшой дождь",
            63: "дождь",
            65: "сильный дождь",
            66: "переохлажденный дождь",
            67: "сильный переохлажденный дождь",
            71: "небольшой снег",
            73: "снег",
            75: "сильный снег",
            77: "снежная крупа",
            80: "ливень",
            81: "ливень",
            82: "сильный ливень",
            85: "снегопад",
            86: "сильный снегопад",
            95: "гроза",
            96: "гроза с градом",
            99: "сильная гроза с градом",
        }

    async def _acquire_rate_limit_slot(self) -> None:
        now = time.monotonic()
        async with self._lock:
            while self._calls and now - self._calls[0] > self.rate_window_s:
                self._calls.popleft()
            if len(self._calls) >= self.rate_limit:
                raise ExternalDataUnavailableError("rate_limited")
            self._calls.append(now)

    async def _get_json(self, path: str, params: dict) -> dict | list:
        if path.startswith("http://") or path.startswith("https://"):
            url = path
        else:
            url = f"{self.base_url}{path}"
        last_error: Optional[Exception] = None

        for attempt in range(self.retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout_s) as client:
                    response = await client.get(url, params=params)
                if response.status_code in {429, 500, 502, 503, 504} and attempt < self.retries:
                    await asyncio.sleep(0.2 * (attempt + 1))
                    continue
                response.raise_for_status()
                return response.json()
            except (httpx.TimeoutException, httpx.ConnectError, httpx.NetworkError) as exc:
                last_error = exc
                if attempt < self.retries:
                    await asyncio.sleep(0.2 * (attempt + 1))
                    continue
                raise ExternalDataUnavailableError("provider_unreachable") from exc
            except httpx.HTTPStatusError as exc:
                last_error = exc
                if exc.response.status_code in {401, 403}:
                    raise ExternalDataUnavailableError("provider_auth_error") from exc
                if exc.response.status_code == 404:
                    raise ExternalDataUnavailableError("city_not_found") from exc
                if exc.response.status_code == 429:
                    raise ExternalDataUnavailableError("provider_rate_limited") from exc
                raise ExternalDataUnavailableError("provider_error") from exc

        if last_error is not None:
            raise ExternalDataUnavailableError("provider_unreachable") from last_error
        raise ExternalDataUnavailableError("provider_error")

    async def _get_open_meteo_city_context(self, city: str) -> CityContext:
        geo_data = await self._get_json(
            "https://geocoding-api.open-meteo.com/v1/search",
            {
                "name": city,
                "count": 1,
                "language": "ru",
            },
        )
        if not isinstance(geo_data, dict):
            raise ExternalDataUnavailableError("provider_bad_response")

        results = geo_data.get("results") or []
        if not isinstance(results, list) or not results:
            return CityContext(
                city=city,
                country=None,
                temperature_c=None,
                weather_description=None,
                source="open-meteo",
                available=False,
                unavailable_reason="city_not_found",
            )

        geo_item = results[0]
        lat = geo_item.get("latitude")
        lon = geo_item.get("longitude")
        if lat is None or lon is None:
            raise ExternalDataUnavailableError("provider_bad_response")

        weather_data = await self._get_json(
            "https://api.open-meteo.com/v1/forecast",
            {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,weather_code",
            },
        )
        if not isinstance(weather_data, dict):
            raise ExternalDataUnavailableError("provider_bad_response")

        current = weather_data.get("current") or {}
        if not isinstance(current, dict):
            raise ExternalDataUnavailableError("provider_bad_response")

        temperature = current.get("temperature_2m")
        weather_code = current.get("weather_code")
        weather_description = self._open_meteo_weather_codes.get(weather_code) if isinstance(weather_code, int) else None

        return CityContext(
            city=geo_item.get("name") or city,
            country=geo_item.get("country_code"),
            temperature_c=float(temperature) if temperature is not None else None,
            weather_description=weather_description,
            source="open-meteo",
            available=True,
        )

    async def get_city_context(self, city: str) -> CityContext:
        if not self.api_key:
            return await self._get_open_meteo_city_context(city)

        await self._acquire_rate_limit_slot()

        geo_data = await self._get_json(
            "/geo/1.0/direct",
            {
                "q": city,
                "limit": 1,
                "appid": self.api_key,
            },
        )
        if not isinstance(geo_data, list) or not geo_data:
            return CityContext(
                city=city,
                country=None,
                temperature_c=None,
                weather_description=None,
                source="openweather",
                available=False,
                unavailable_reason="city_not_found",
            )

        geo_item = geo_data[0]
        lat = geo_item.get("lat")
        lon = geo_item.get("lon")
        if lat is None or lon is None:
            raise ExternalDataUnavailableError("provider_bad_response")

        weather_data = await self._get_json(
            "/data/2.5/weather",
            {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric",
                "lang": "ru",
            },
        )
        if not isinstance(weather_data, dict):
            raise ExternalDataUnavailableError("provider_bad_response")

        weather_items = weather_data.get("weather") or []
        description = None
        if isinstance(weather_items, list) and weather_items:
            first_item = weather_items[0]
            if isinstance(first_item, dict):
                description = first_item.get("description")

        main = weather_data.get("main") or {}
        temperature = main.get("temp") if isinstance(main, dict) else None

        return CityContext(
            city=geo_item.get("name") or city,
            country=geo_item.get("country"),
            temperature_c=float(temperature) if temperature is not None else None,
            weather_description=description,
            source="openweather",
            available=True,
        )
