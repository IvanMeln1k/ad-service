from fastapi import Request

from src.services.service import RegistrationService


def get_registration_service(request: Request) -> RegistrationService:
    return request.app.state.registration_service
