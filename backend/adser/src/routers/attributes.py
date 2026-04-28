from fastapi import APIRouter, Depends, Query

from src.auth import get_current_user, AuthUser

router = APIRouter()

ATTRIBUTE_RESOLVERS = {
    "can_create_ad": lambda user: user.email_confirmed and "MODERATOR" not in user.roles and "ADMIN" not in user.roles,
    "can_moderate": lambda user: "MODERATOR" in user.roles or "ADMIN" in user.roles,
}


@router.get("/api/v1/attributes")
async def get_attributes(
    attrs: str = Query(..., description="Comma-separated list of attributes"),
    user: AuthUser = Depends(get_current_user),
):
    requested = [a.strip() for a in attrs.split(",") if a.strip()]
    result = {}
    for attr in requested:
        resolver = ATTRIBUTE_RESOLVERS.get(attr)
        if resolver is not None:
            result[attr] = resolver(user)
    return result
