from fastapi import FastAPI

from src.config import config
from src.sender.smtp_sender import SmtpEmailSender
from src.services.notification_service import NotificationServiceImpl
from src.routers import send_email

app = FastAPI(title="Notificator Service", version="1.0.0")

sender = SmtpEmailSender(
    host=config.SMTP_HOST,
    port=config.SMTP_PORT,
    user=config.SMTP_USER,
    password=config.SMTP_PASS,
    from_addr=config.SMTP_FROM,
)
app.state.notification_service = NotificationServiceImpl(sender=sender)

app.include_router(send_email.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
