import logging
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.config import config
from src.repository.postgres_repository import PostgresAuthRepository
from src.services.auth_service import AuthenticationService
from src.services.services import Tokens, UserAlreadyExistsError, UserNotFoundError, InvalidCredentialsError, InvalidRefreshTokenError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Authentication Service", version="1.0.0")

engine = create_async_engine(config.database_url)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

auth_repository = PostgresAuthRepository()
auth_service = AuthenticationService(
    repository=auth_repository,
    jwt_secret=config.JWT_SECRET,
    access_token_ttl=config.ACCESS_TOKEN_TTL,
    refresh_token_ttl=config.REFRESH_TOKEN_TTL
)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@app.post("/users", response_model=Tokens)
async def create_user(
    user_id: str,
    password: str,
    session: AsyncSession = Depends(get_db)
):
    try:
        tokens = await auth_service.create_user(session, user_id, password)
        return tokens
    except UserAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.post("/tokens", response_model=Tokens)
async def create_token(
    user_id: str,
    password: str,
    session: AsyncSession = Depends(get_db)
):
    try:
        tokens = await auth_service.authenticate_user(session, user_id, password)
        return tokens
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.put("/tokens", response_model=Tokens)
async def refresh_token(
    refresh_token: str,
    session: AsyncSession = Depends(get_db)
):
    try:
        tokens = await auth_service.refresh_tokens(session, refresh_token)
        return tokens
    except InvalidRefreshTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.delete("/tokens")
async def delete_tokens(
    user_id: str,
    refresh_tokens: list[str] = None,
    except_token: str = None,
    session: AsyncSession = Depends(get_db)
):
    try:
        deleted_count = await auth_service.delete_refresh_tokens(
            session, user_id, refresh_tokens, except_token
        )
        return {"deleted_tokens": deleted_count}
    except Exception as e:
        logger.error(f"Delete tokens error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: str,
    session: AsyncSession = Depends(get_db)
):
    try:
        await auth_service.delete_user(session, user_id)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except Exception as e:
        logger.error(f"Delete user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.put("/users/{user_id}/password", response_model=Tokens)
async def change_password(
    user_id: str,
    old_password: str,
    new_password: str,
    session: AsyncSession = Depends(get_db)
):
    try:
        tokens = await auth_service.change_password(session, user_id, old_password, new_password)
        return tokens
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    except Exception as e:
        logger.error(f"Password change error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
