import logging
import uuid

from src.clients.auther_client import (
    AutherClient,
    InvalidCredentialsError as AutherInvalidCredentials,
)
from src.clients.profiler_client import ProfilerClient, EmailAlreadyTakenError as ClientEmailTaken
from src.services.service import (
    RegistrationService,
    RegistrationResult,
    LoginResult,
    EmailAlreadyTakenError,
    InvalidCredentialsError,
    InvalidTokenError,
)

logger = logging.getLogger(__name__)


class RegistrationServiceImpl(RegistrationService):
    def __init__(
        self,
        auther_client: AutherClient,
        profiler_client: ProfilerClient,
    ):
        self.auther_client = auther_client
        self.profiler_client = profiler_client

    async def register(self, email: str, name: str, password: str) -> RegistrationResult:
        user_id = str(uuid.uuid4())

        # Step 1: Create credentials in Auther
        tokens = await self.auther_client.create_user(user_id, password)

        # Step 2: Create profile in Profiler
        try:
            await self.profiler_client.create_profile(user_id, name, email)
        except ClientEmailTaken:
            # Compensation: rollback Auther
            logger.warning("Email %s already taken, compensating auther for user %s", email, user_id)
            await self.auther_client.delete_user(user_id)
            raise EmailAlreadyTakenError(f"Email {email} already taken")

        return RegistrationResult(
            user_id=user_id,
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            refresh_token_expires_at=tokens.refresh_token_expires_at,
        )

    async def login(self, email: str, password: str) -> LoginResult:
        # Step 1: Find user_id by email in Profiler
        profiles = await self.profiler_client.lookup_by_email(email)
        if not profiles:
            raise InvalidCredentialsError("Invalid email or password")

        user_id = profiles[0]["user_id"]

        # Step 2: Authenticate in Auther
        try:
            tokens = await self.auther_client.authenticate(user_id, password)
        except AutherInvalidCredentials:
            raise InvalidCredentialsError("Invalid email or password")

        return LoginResult(
            user_id=user_id,
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            refresh_token_expires_at=tokens.refresh_token_expires_at,
        )

    async def logout(self, user_id: str, refresh_token: str) -> None:
        await self.auther_client.delete_refresh_tokens(user_id, [refresh_token])

    async def confirm_email(self, token: str) -> None:
        try:
            await self.profiler_client.confirm_email(token)
        except ValueError as e:
            raise InvalidTokenError(str(e)) from e
        except ClientEmailTaken:
            raise EmailAlreadyTakenError("Email already confirmed")
