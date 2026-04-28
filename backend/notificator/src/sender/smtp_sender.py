from email.message import EmailMessage

import aiosmtplib

from src.sender.sender import EmailSender


class SmtpEmailSender(EmailSender):
    def __init__(
        self, host: str, port: int, user: str, password: str, from_addr: str
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.from_addr = from_addr

    async def send(self, to: str, subject: str, body: str) -> None:
        message = EmailMessage()
        message["From"] = self.from_addr
        message["To"] = to
        message["Subject"] = subject
        message.set_content(body, subtype="html")

        await aiosmtplib.send(
            message,
            hostname=self.host,
            port=self.port,
            username=self.user or None,
            password=self.password or None,
            start_tls=True,
        )
