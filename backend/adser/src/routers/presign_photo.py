import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import get_current_user, AuthUser
from src.clients.s3_client import S3Client
from src.config import config
from src.dependencies import get_ads_service, get_session, get_s3_client
from src.schemas.schemas import PresignResponse, PresignPhotoRequest
from src.services.service import AdsService, AdNotFoundError

router = APIRouter()


@router.post("/api/v1/ads/{ad_id}/photos/presign", response_model=PresignResponse)
async def presign_photo(
    ad_id: str,
    request: PresignPhotoRequest,
    user: AuthUser = Depends(get_current_user),
    service: AdsService = Depends(get_ads_service),
    session: AsyncSession = Depends(get_session),
    s3: S3Client = Depends(get_s3_client),
):
    try:
        ad = await service.get_ad(session, ad_id)
        if ad.user_id != user.user_id:
            raise HTTPException(status_code=403, detail="Not the owner")
    except AdNotFoundError:
        raise HTTPException(status_code=404, detail="Ad not found")

    if request.content_type not in config.ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported content_type")
    if request.file_size > config.MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File is too large")

    extension_by_content_type = {
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/webp": "webp",
    }
    extension = extension_by_content_type[request.content_type]

    s3_key = f"ads/{ad_id}/{uuid.uuid4()}.{extension}"
    upload_url = s3.generate_presigned_put(s3_key, request.content_type)

    return PresignResponse(upload_url=upload_url, s3_key=s3_key, max_file_size=config.MAX_IMAGE_SIZE_BYTES)
