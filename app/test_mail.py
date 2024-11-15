import asyncio
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

# Set up email configuration directly
conf = ConnectionConfig(
    MAIL_USERNAME="kehindeadekola96@gmail.com",
    MAIL_PASSWORD="vgfoqejwlhijkftm",  # Replace with your actual password
    MAIL_FROM="kehindeadekola96@gmail.com",
    MAIL_PORT=587,  # Gmail's SMTP server port for TLS
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

# Function to send a simple test email
async def send_test_email():
    message = MessageSchema(
        subject="Test Email",
        recipients=["kehindeadekola03@gmail.com"],  # List of recipients
        body="This is a test email. Just checking if this works!",
        subtype="plain"  # Plain text email
    )
    fm = FastMail(conf)
    await fm.send_message(message)

# Run the async function in an event loop
asyncio.run(send_test_email())


# To test, call send_test_email within your FastAPI application
# Example usage:
# await send_test_email()
