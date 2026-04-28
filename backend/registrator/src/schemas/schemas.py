from typing import Optional
import datetime

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    name: str
    password: str


class TokenInfo(BaseModel):
    token: str
    expires_at: Optional[datetime.datetime] = None


class RegisterResponse(BaseModel):
    user_id: str
    access_token: str
    refresh_token: TokenInfo


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    user_id: str
    access_token: str
    refresh_token: TokenInfo


class LogoutRequest(BaseModel):
    user_id: str
    refresh_token: str


class ConfirmEmailRequest(BaseModel):
    token: str
