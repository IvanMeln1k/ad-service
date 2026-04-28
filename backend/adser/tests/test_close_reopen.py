from httpx import AsyncClient
from tests.conftest import AUTH_HEADERS


async def test_close_and_reopen(client: AsyncClient):
    create = await client.post(
        "/api/v1/ads",
        json={"title": "Test title", "description": "Long enough description to test close and reopen"},
        headers=AUTH_HEADERS,
    )
    ad_id = create.json()["id"]

    # Close
    response = await client.post(f"/api/v1/ads/{ad_id}/close", headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert response.json()["status"] == "closed"

    # Verify closed
    ad = await client.get(f"/api/v1/ads/{ad_id}")
    assert ad.json()["status"] == "CLOSED"

    # Reopen
    response = await client.post(f"/api/v1/ads/{ad_id}/reopen", headers=AUTH_HEADERS)
    assert response.status_code == 200

    # Verify active again
    ad = await client.get(f"/api/v1/ads/{ad_id}")
    assert ad.json()["status"] == "ACTIVE"


async def test_close_already_closed(client: AsyncClient):
    create = await client.post(
        "/api/v1/ads",
        json={"title": "Test title", "description": "Long enough description to test close and reopen"},
        headers=AUTH_HEADERS,
    )
    ad_id = create.json()["id"]

    await client.post(f"/api/v1/ads/{ad_id}/close", headers=AUTH_HEADERS)
    response = await client.post(f"/api/v1/ads/{ad_id}/close", headers=AUTH_HEADERS)
    assert response.status_code == 409
