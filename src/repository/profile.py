from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.conf import messages
from src.repository.users import get_user_by_username, get_user_by_email, clear_user_cache, get_user_by_id
from src.database.models import User, Comment, Image, Role
from src.schemas.users import UpdateFullProfile, ProfileResponse


async def read_profile(user: User, db: Session) -> ProfileResponse:
    """
    Retrieves a user profile.

    :param user: given user.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: All information about user.
    :rtype: ProfileResponse
    """
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND)

    comments_count = db.query(func.count(Comment.id)).filter(Comment.user_id == user.id).scalar()
    images_count = db.query(func.count(Image.id)).filter(Image.user_id == user.id).scalar()
    result = ProfileResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        avatar=user.avatar,
        role=user.role,
        created_at=user.created_at,
        comments_count=comments_count,
        images_count=images_count,
    )
    return result


async def update_profile(data: UpdateFullProfile, user: User, db: Session) -> bool:
    """
    Update user profile in the database.

    :param data: Data to update the profile.
    :type data: UpdateFullProfile
    :param user: The user to update.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: True if the profile was updated, None otherwise.
    :rtype: bool | None
    """
    if user:
        if data.username:
            new_user = await get_user_by_username(str(data.username), db)
            if not new_user:
                user.username = str(data.username)

        if data.email:
            existing_user = await get_user_by_email(str(data.email), db)
            if not existing_user or existing_user.id == user.id:
                user.email = str(data.email)
        db.add(user)
        db.commit()
        db.refresh(user)
        clear_user_cache(user)
        return True

    return False


async def change_role(user_id: int, role_user: Role, db: Session) -> bool:
    """
    Update user profile by admin.

    :param user_id: The id of the user to update.
    :type user_id: int
    :param role_user: The role of the user to update.
    :type role_user: Role
    :param db: The database session.
    :type db: Session
    :return: True if the profile was updated, False otherwise.
    :rtype: bool
    """
    user_to_update = await get_user_by_id(user_id, db)
    if user_to_update and user_to_update.role != role_user:
        user_to_update.role = role_user
        db.commit()
        return True
    return False
