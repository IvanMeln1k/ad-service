import datetime
from typing import Optional

from pydantic import BaseModel


class CreateProfileRequest(BaseModel):
    user_id: str
    name: str
    email: str


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None


class RoleResponse(BaseModel):
    role: str
    assigned_at: Optional[datetime.datetime] = None


class ProfileResponse(BaseModel):
    user_id: str
    name: str
    city: Optional[str] = None
    email: str
    email_confirmed: bool = False
    avatar_url: Optional[str] = None
    roles: list[RoleResponse] = []
    created_at: Optional[datetime.datetime] = None


class ProfileLookupItem(BaseModel):
    user_id: str
    name: str
    avatar_url: Optional[str] = None


class ConfirmEmailRequest(BaseModel):
    token: str


class EmailConfirmationTokenResponse(BaseModel):
    token: str
