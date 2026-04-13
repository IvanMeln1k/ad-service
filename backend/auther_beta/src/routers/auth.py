from email_validator import EmailNotValidError, validate_email
from fastapi import APIRouter, Cookie, Depends, Response
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_async_session
from src.routers.dependencies import get_users_service
from src.schemas.users import UserAuthSchema, UserCreateSchema, UserReturnSchema
from src.service.users import UsersService

auth_router = APIRouter(prefix="/auth")


class InvalidEmail(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Invalid email")


class Tokens(BaseModel):
    access_token: str
    refresh_token: str


class SignUpResponseSchema(BaseModel):
    tokens: Tokens


def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False


@auth_router.post("/sign-up", status_code=201)
async def sign_up(
    response: Response,
    user: UserCreateSchema,
    user_service: UsersService = Depends(get_users_service),
    session: AsyncSession = Depends(get_async_session),
) -> SignUpResponseSchema:
    if not is_valid_email(user.email):
        raise InvalidEmail
    tokens = await user_service.create_user(session, user)
    response.set_cookie(
        key="refresh_token", value=tokens["refresh_token"], httponly=True
    )
    return SignUpResponseSchema(tokens=tokens)


class VerifyResponseSchema(BaseModel):
    verified: bool


@auth_router.get("/verify")
async def verify(
    token: str,
    user_service: UsersService = Depends(get_users_service),
    session: AsyncSession = Depends(get_async_session),
) -> VerifyResponseSchema:
    await user_service.verify_email_user(session, token)
    return VerifyResponseSchema(verified=True)


class SignInResponseSchema(BaseModel):
    user: UserReturnSchema
    tokens: Tokens


@auth_router.post("/sign-in")
async def sign_in(
    response: Response,
    user: UserAuthSchema,
    user_service: UsersService = Depends(get_users_service),
    session: AsyncSession = Depends(get_async_session),
) -> SignInResponseSchema:
    res = await user_service.auth_user(session, user)
    response.set_cookie(
        key="refresh_token", value=res["tokens"]["refresh_token"], httponly=True
    )
    return res


class RefreshResponseSchema(BaseModel):
    tokens: Tokens


class InvalidRefreshToken(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Invalid refresh token")


@auth_router.post("/refresh")
async def refresh(
    response: Response,
    user_service: UsersService = Depends(get_users_service),
    session: AsyncSession = Depends(get_async_session),
    refresh_token: str | None = Cookie(default=None),
) -> RefreshResponseSchema:
    if refresh_token is None:
        raise InvalidRefreshToken
    tokens = await user_service.refresh_tokens(session, refresh_token=refresh_token)
    response.set_cookie(
        key="refresh_token", value=tokens["refresh_token"], httponly=True
    )
    return RefreshResponseSchema(tokens=tokens)
