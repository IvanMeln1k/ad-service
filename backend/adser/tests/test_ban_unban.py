from httpx import AsyncClient
from tests.conftest import AUTH_HEADERS


async def test_ban_and_unban(client: AsyncClient, fake_auth):
    # Create ad
    create = await client.post(
        "/api/v1/ads",
        json={"title": "Test title", "description": "Long enough description for moderation flow"},
        headers=AUTH_HEADERS,
    )
    ad_id = create.json()["id"]

    # Set moderator role
    fake_auth.user.roles = ["MODERATOR"]

    # Ban
    response = await client.post(
        f"/api/v1/ads/{ad_id}/ban",
        json={"reason": "Spam"},
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    assert response.json()["reason"] == "Spam"

    # Unban
    response = await client.post(
        f"/api/v1/ads/{ad_id}/unban",
        json={"unban_reason": "Reviewed"},
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200

    # Get bans
    response = await client.get(f"/api/v1/ads/{ad_id}/bans", headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["unbanned_at"] is not None


async def test_ban_without_moderator_role(client: AsyncClient, fake_auth):
    create = await client.post(
        "/api/v1/ads",
        json={"title": "Test title", "description": "Long enough description for moderation flow"},
        headers=AUTH_HEADERS,
    )
    ad_id = create.json()["id"]

    fake_auth.user.roles = []
    response = await client.post(
        f"/api/v1/ads/{ad_id}/ban",
        json={"reason": "Spam"},
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 403
