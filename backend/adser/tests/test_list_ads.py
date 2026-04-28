from httpx import AsyncClient
from tests.conftest import AUTH_HEADERS


async def test_list_ads_empty(client: AsyncClient):
    response = await client.get("/api/v1/ads")
    assert response.status_code == 200
    payload = response.json()
    assert payload["items"] == []
    assert payload["total"] == 0


async def test_list_ads_with_data(client: AsyncClient):
    await client.post("/api/v1/ads", json={"title": "Ad 1", "description": "Description for ad one"}, headers=AUTH_HEADERS)
    await client.post("/api/v1/ads", json={"title": "Ad 2", "description": "Description for ad two"}, headers=AUTH_HEADERS)

    response = await client.get("/api/v1/ads")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["items"]) == 2
    assert payload["total"] == 2


async def test_get_ad_not_found(client: AsyncClient):
    response = await client.get("/api/v1/ads/nonexistent-id")
    assert response.status_code == 404


async def test_list_ads_with_filters_sort_and_pagination(client: AsyncClient):
    await client.post(
        "/api/v1/ads",
        json={"title": "Bike", "description": "Fast bike description", "price": 100, "city": "Moscow", "category": "AUTO"},
        headers=AUTH_HEADERS,
    )
    await client.post(
        "/api/v1/ads",
        json={"title": "Laptop", "description": "Gaming laptop description", "price": 200, "city": "Kazan", "category": "ELECTRONICS"},
        headers=AUTH_HEADERS,
    )

    response = await client.get(
        "/api/v1/ads?city=mos&price_min=50&price_max=150&sort_by=price&sort_order=asc&limit=1&offset=0"
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert len(payload["items"]) == 1
    assert payload["items"][0]["title"] == "Bike"
