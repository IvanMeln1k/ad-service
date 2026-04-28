from fastapi import Request

from src.services.service import NotificationService


def get_notification_service(request: Request) -> NotificationService:
    return request.app.state.notification_service
