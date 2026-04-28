from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.config import config
from src.events.kafka_publisher import KafkaEventPublisher
from src.repository.postgres_repository import PostgresProfileRepository
from src.services.profile_service import ProfileServiceImpl
from src.services.roles_service import RolesServiceImpl
from src.services.email_confirmation_service import EmailConfirmationServiceImpl
from src.auth import JwtAuthProvider
from src.routers import (
    create_profile,
    list_profiles,
    lookup_profile,
    get_profile,
    update_profile,
    delete_profile,
    get_roles,
    manage_roles,
    email_confirmation_token,
    confirm_email,
)

publisher = KafkaEventPublisher(bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await publisher.start()
    yield
    await publisher.stop()


app = FastAPI(title="Profiler Service", version="1.0.0", lifespan=lifespan)

engine = create_async_engine(config.database_url)
app.state.session_factory = async_sessionmaker(engine, expire_on_commit=False)

repository = PostgresProfileRepository()
app.state.profile_service = ProfileServiceImpl(repository=repository, publisher=publisher)
app.state.roles_service = RolesServiceImpl(repository=repository)
app.state.email_service = EmailConfirmationServiceImpl(repository=repository)
app.state.auth_provider = JwtAuthProvider()

# Static paths first, then parameterized
app.include_router(create_profile.router)
app.include_router(list_profiles.router)
app.include_router(lookup_profile.router)
app.include_router(confirm_email.router)
app.include_router(get_profile.router)
app.include_router(update_profile.router)
app.include_router(delete_profile.router)
app.include_router(get_roles.router)
app.include_router(manage_roles.router)
app.include_router(email_confirmation_token.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
