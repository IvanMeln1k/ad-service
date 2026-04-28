from fastapi import FastAPI

from src.config import config
from src.clients.auther_client import HttpAutherClient
from src.clients.profiler_client import HttpProfilerClient
from src.services.registration_service import RegistrationServiceImpl
from src.routers import register, login, logout, confirm_email

app = FastAPI(title="Registrator Service", version="1.0.0")

auther_client = HttpAutherClient(base_url=config.AUTHER_URL)
profiler_client = HttpProfilerClient(base_url=config.PROFILER_URL)
app.state.registration_service = RegistrationServiceImpl(
    auther_client=auther_client,
    profiler_client=profiler_client,
)

app.include_router(register.router)
app.include_router(login.router)
app.include_router(logout.router)
app.include_router(confirm_email.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
