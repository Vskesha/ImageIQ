import cloudinary
import cloudinary.uploader

from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.config import settings
from src.schemas.users import UserResponse
from src.services.cloud_image import CloudImage
from src.conf import messages
from typing import Optional
from src.services.role import allowed_admin_moderator


router = APIRouter(prefix="/users", tags=["users"])
security = HTTPBearer()

@router.get("/me/", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(auth_service.token_manager.get_current_user)):
    """
    The read_users_me function is a GET request that returns the current user's information.
        It requires an authorization token to be passed in the header of the request.

    :param current_user: User: Get the current user
    :return: The current user
    """
    return current_user


@router.patch('/avatar', response_model=UserResponse)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth_service.token_manager.get_current_user),
                             db: Session = Depends(get_db)):
    """
    The update_avatar_user function updates the avatar of a user.
        The function takes in an UploadFile object, which is a file that has been uploaded to the server.
        It also takes in a User object and Session object as dependencies.

    :param file: UploadFile: Upload the file to cloudinary
    :param current_user: User: Get the current user
    :param db: Session: Get the database session
    :return: A user object
    """
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )
    public_id = CloudImage.generate_name_avatar(current_user.email)
    r = CloudImage.upload(file.file, public_id)
    src_url = CloudImage.get_url_for_avatar(public_id, r)
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user


@router.patch(
              '/ban_user/{user_id}/{active_status}', response_model=UserResponse,
              dependencies=[Depends(allowed_admin_moderator)],
              description='Ban/unban user'
              )
async def ban_user(
                   id: int,
                   active_status: bool,
                   current_user: dict = Depends(auth_service.token_manager.get_current_user),
                   credentials: HTTPAuthorizationCredentials = Security(security),
                   db: Session = Depends(get_db)
                   ) -> User:
    """
    The ban_user function is used to ban a user from the system.

    :param user_id: int: Identify the user to be banned
    :param active_status: bool: Set the user's status to active or inactive
    :param current_user: dict: Get the current user from the authuser class
    :param db: Session: Access the database
    :return: The banned user object
    :doc-author: Trelent
    """
    user: Optional[User] = await repository_users.ban_user(id, active_status, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_USER_NOT_FOUND)

    await auth_service.token_manager.clear_user_cash(user.email)

    return user