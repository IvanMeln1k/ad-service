from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_profile_service, get_session
from src.schemas.schemas import CreateProfileRequest
from src.services.services import ProfileService

router = APIRouter()


@router.post("/api/v1/profile", status_code=201)
async def create_profile(
    request: CreateProfileRequest,
    service: ProfileService = Depends(get_profile_service),
    session: AsyncSession = Depends(get_session),
):
    try:
        await service.create_profile(session, request.user_id, request.name, request.email)
        return {"user_id": request.user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
