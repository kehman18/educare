from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
import os

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT")),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

async def send_verification_email(email: EmailStr, token: int):
    message = MessageSchema(
        subject="Email Verification",
        recipients=[email],
        body=f"Your verification code is: {token}. It will expire in 1 minute.",
        subtype="plain"
    )
    fm = FastMail(conf)
    await fm.send_message(message)
