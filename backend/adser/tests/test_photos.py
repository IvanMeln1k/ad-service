from httpx import AsyncClient
from tests.conftest import AUTH_HEADERS


async def test_add_and_delete_photo(client: AsyncClient):
    create = await client.post(
        "/api/v1/ads",
        json={"title": "Test title", "description": "Long enough description for this ad"},
        headers=AUTH_HEADERS,
    )
    ad_id = create.json()["id"]

    # Add photo
    response = await client.post(
        f"/api/v1/ads/{ad_id}/photos",
        json={"s3_key": "ads/test/photo.jpg", "position": 0},
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 201
    photo_id = response.json()["id"]

    # Verify photo in ad
    ad = await client.get(f"/api/v1/ads/{ad_id}")
    assert len(ad.json()["photos"]) == 1

    # Delete photo
    response = await client.delete(f"/api/v1/ads/{ad_id}/photos/{photo_id}", headers=AUTH_HEADERS)
    assert response.status_code == 204


async def test_presign_photo_validation(client: AsyncClient):
    create = await client.post(
        "/api/v1/ads",
        json={"title": "Test title", "description": "Long enough description"},
        headers=AUTH_HEADERS,
    )
    ad_id = create.json()["id"]

    ok = await client.post(
        f"/api/v1/ads/{ad_id}/photos/presign",
        json={"file_name": "image.jpg", "content_type": "image/jpeg", "file_size": 1000},
        headers=AUTH_HEADERS,
    )
    assert ok.status_code == 200
    assert "upload_url" in ok.json()
    assert ok.json()["max_file_size"] > 0

    bad_type = await client.post(
        f"/api/v1/ads/{ad_id}/photos/presign",
        json={"file_name": "file.txt", "content_type": "text/plain", "file_size": 1000},
        headers=AUTH_HEADERS,
    )
    assert bad_type.status_code == 400
