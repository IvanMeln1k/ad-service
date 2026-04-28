from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import get_current_user, AuthUser
from src.dependencies import get_ads_service, get_session
from src.schemas.schemas import ConfirmPhotoRequest, PhotoResponse
from src.services.service import AdsService, AdNotFoundError, NotOwnerError

router = APIRouter()


@router.post("/api/v1/ads/{ad_id}/photos", response_model=PhotoResponse, status_code=201)
async def confirm_photo(
    ad_id: str,
    request: ConfirmPhotoRequest,
    user: AuthUser = Depends(get_current_user),
    service: AdsService = Depends(get_ads_service),
    session: AsyncSession = Depends(get_session),
):
    try:
        photo = await service.add_photo(session, ad_id, user.user_id, request.s3_key, request.position)
        return PhotoResponse(id=photo.id, s3_key=photo.s3_key, position=photo.position)
    except AdNotFoundError:
        raise HTTPException(status_code=404, detail="Ad not found")
    except NotOwnerError:
        raise HTTPException(status_code=403, detail="Not the owner")
