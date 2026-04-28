import pytest


@pytest.mark.asyncio
async def test_robots_txt(client):
    response = await client.get("/api/v1/seo/robots.txt")
    assert response.status_code == 200
    assert "Sitemap:" in response.text
    assert "Disallow: /profile" in response.text


@pytest.mark.asyncio
async def test_sitemap_xml_contains_public_routes(client, fake_repo):
    ad = await fake_repo.create_ad(
        session=None,
        user_id="user-1",
        title="SEO ad",
        description="SEO ad description that is long enough",
        price=100.0,
        city="Moscow",
        category="OTHER",
    )

    response = await client.get("/api/v1/seo/sitemap.xml")
    assert response.status_code == 200
    assert "/ads" in response.text
    assert f"/ads/{ad.id}" in response.text
