from pydantic import BaseModel, EmailStr


class SendEmailRequest(BaseModel):
    to: EmailStr
    subject: str
    body: str


class SendEmailResponse(BaseModel):
    status: str
