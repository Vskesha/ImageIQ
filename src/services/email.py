from datetime import datetime
import traceback
from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr
from src.services.auth import auth_service
from src.conf.config import settings
from src.conf import messages
from src.services.asyncdevlogging import async_logging_to_file

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME="APP Contacts",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    The send_email function sends an email to the user with a link to confirm their email address.
        The function takes in three parameters:
            -email: EmailStr, the user's email address.
            -username: str, the username of the user who is registering for an account.  This will be used in a greeting message within the body of the email sent to them.
            -host: str, this is where we are hosting our application (i.e., localhost).  This will be used as part of a URL that users can click on within their emails.

    :param email: EmailStr: Check if the email is valid
    :param username: str: Pass the username to the template
    :param host: str: Pass the hostname of the server to the template
    :return: A coroutine object
    """
    try:
        token_verification = auth_service.token_manager.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        await async_logging_to_file(
            f'\n500:\t{datetime.now()}\t{messages.MSC500_SENDING_EMAIL}: {err}\t{traceback.extract_stack(None, 2)[1][2]}')


async def send_new_password(email: EmailStr, username: str, host: str, password: str):
    """
    The send_new_password function sends an email to the user with their new password.
        Args:
            email (str): The user's email address.
            username (str): The user's username.
            host (str): The hostname of the server where this function is being called from, e.g., 'localhost'.  This is used in constructing a URL for the login page that will be included in the message body of this function's output, so that users can easily click on it and log into their account using their new password without having to copy/paste or type anything manually.

    :param email: EmailStr: Specify the email address of the user who is requesting a new password
    :param username: str: Get the username of the user who requested a password reset
    :param host: str: Pass the host name to the template
    :param password: str: Send the new password to the user
    :return: A string
    :doc-author: Trelent
    """
    try:
        message = MessageSchema(
            subject=messages.PASSWORD_RESET_REQUEST,
            recipients=[email],
            template_body={"host": host, "username": username, "new_password": password},
            subtype=MessageType.html
        )
        fm = FastMail(conf)
        await fm.send_message(message, template_name="new_password.html")
    except ConnectionErrors as err:
        await async_logging_to_file(
            f'\n500:\t{datetime.now()}\t{messages.MSC500_SENDING_EMAIL}: {err}\t{traceback.extract_stack(None, 2)[1][2]}')


async def send_reset_password(email: EmailStr, username: str, host: str):
    """
    The send_reset_password function is used to send a password reset email to the user.
        Args:
            email (str): The user's email address.
            username (str): The user's username.
            host (str): The host of the application, e.g., http://localhost:8000/api/v2/.

    :param email: EmailStr: Specify the email address of the user who is requesting a password reset
    :param username: str: Create the message that will be sent to the user
    :param host: str: Create a link to the password reset page
    :return: A message that the email was sent successfully
    :doc-author: Trelent
    """
    try:
        token_verification = auth_service.token_manager.create_email_token({"sub": email})
        message = MessageSchema(
            subject=messages.PASSWORD_RESET_REQUEST,
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )
        fm = FastMail(conf)
        await fm.send_message(message, template_name="password_reset.html")
    except ConnectionErrors as err:
        await async_logging_to_file(
            f'\n500:\t{datetime.now()}\t{messages.MSC500_SENDING_EMAIL}: {err}\t{traceback.extract_stack(None, 2)[1][2]}')