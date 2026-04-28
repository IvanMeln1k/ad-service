from xml.sax.saxutils import escape

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import config
from src.dependencies import get_ads_service, get_session
from src.services.service import AdsService

router = APIRouter()


@router.get("/api/v1/seo/robots.txt")
async def robots_txt():
    content = (
        "User-agent: *\n"
        "Allow: /ads\n"
        "Disallow: /login\n"
        "Disallow: /register\n"
        "Disallow: /profile\n"
        "Disallow: /ads/new\n"
        "Disallow: /confirm-email\n"
        "Disallow: /api/\n\n"
        f"Sitemap: {config.PUBLIC_SITE_URL.rstrip('/')}/sitemap.xml\n"
    )
    return Response(content=content, media_type="text/plain")


@router.get("/api/v1/seo/sitemap.xml")
async def sitemap_xml(
    service: AdsService = Depends(get_ads_service),
    session: AsyncSession = Depends(get_session),
):
    ads, _ = await service.list_ads(
        session=session,
        limit=1000,
        offset=0,
        include_banned=False,
        sort_by="created_at",
        sort_order="desc",
    )

    base_url = config.PUBLIC_SITE_URL.rstrip("/")
    urls = [f"{base_url}/ads"] + [f"{base_url}/ads/{ad.id}" for ad in ads]

    xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in urls:
        xml_lines.append("  <url>")
        xml_lines.append(f"    <loc>{escape(url)}</loc>")
        xml_lines.append("  </url>")
    xml_lines.append("</urlset>")
    return Response(content="\n".join(xml_lines), media_type="application/xml")
