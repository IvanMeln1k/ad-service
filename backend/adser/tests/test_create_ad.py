from httpx import AsyncClient
from tests.conftest import AUTH_HEADERS


async def test_create_ad_success(client: AsyncClient, fake_repo):
    response = await client.post(
        "/api/v1/ads",
        json={"title": "Selling bike", "description": "Good condition bike with low mileage", "price": 12000, "city": "Moscow", "category": "AUTO"},
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Selling bike"
    assert data["price"] == 12000
    assert data["city"] == "Moscow"
    assert data["category"] == "AUTO"
    assert data["status"] == "ACTIVE"
    assert len(fake_repo.ads) == 1


async def test_create_ad_no_auth(client: AsyncClient):
    response = await client.post(
        "/api/v1/ads",
        json={"title": "Test title", "description": "Test description value"},
    )
    assert response.status_code == 401


async def test_create_ad_email_not_confirmed(client: AsyncClient, fake_auth):
    fake_auth.user.email_confirmed = False
    response = await client.post(
        "/api/v1/ads",
        json={"title": "Test title", "description": "Test description value"},
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Email not confirmed"


async def test_create_ad_validation_error(client: AsyncClient):
    response = await client.post(
        "/api/v1/ads",
        json={"title": "ab", "description": "short"},
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 422


async def test_create_ad_forbidden_for_moderator(client: AsyncClient, fake_auth):
    fake_auth.user.roles = ["MODERATOR"]
    fake_auth.user.email_confirmed = True
    response = await client.post(
        "/api/v1/ads",
        json={"title": "Test title", "description": "Test description value"},
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Staff users cannot create ads"
