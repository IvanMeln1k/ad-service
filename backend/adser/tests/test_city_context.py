import pytest


@pytest.mark.asyncio
async def test_city_context_success(client):
    response = await client.get("/api/v1/external/city-context", params={"city": "Moscow"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["available"] is True
    assert payload["city"] == "Moscow"
    assert payload["source"] == "openweather"
    assert payload["temperature_c"] == 16.5


@pytest.mark.asyncio
async def test_city_context_not_found(client):
    response = await client.get("/api/v1/external/city-context", params={"city": "Atlantis"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["available"] is False
    assert payload["unavailable_reason"] == "city_not_found"


@pytest.mark.asyncio
async def test_city_context_validation(client):
    response = await client.get("/api/v1/external/city-context", params={"city": "A"})
    assert response.status_code == 422
