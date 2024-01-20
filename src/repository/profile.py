from libgravatar import Gravatar
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.repository.users import get_user_by_username, get_user_by_email, clear_user_cache, get_user_by_id
from src.database.models import User, Comment, Image, Role
from src.schemas.users import UpdateProfile


async def read_profile(user: User, db: Session) -> dict:
    """
    Retrieves a user profile.

    :param user: given user.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The user.
    :rtype: User
    """
    result = {}
    if user:
        comments_count = db.query(func.count(Comment.id)).filter(Comment.user_id == user.id).scalar()
        images_count = db.query(func.count(Image.id)).filter(Image.user_id == user.id).scalar()
        result = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "avatar": user.avatar,
            "role": user.role,
            "created_at": user.created_at,
            "comments_count": comments_count,
            "images_count": images_count,
        }
    return result


async def update_profile(data: UpdateProfile, user: User, db: Session) -> bool | None:
    """
    Update user profile in the database.

    :param data: Data to update the profile.
    :type data: UpdateProfile
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

        db.commit()
        clear_user_cache(user)
        return True

    return None


async def update_profile_by_admin(user_id: int, role_user: Role, db: Session) -> bool | None:
    """
    Update user profile by admin.

    :param user_id: The id of the user to update.
    :type user_id: int
    :param role_user: The role of the user to update.
    :type role_user: Role
    :param db: The database session.
    :type db: Session
    :return: True if the profile was updated, None otherwise.
    :rtype: bool | None
    """
    user_to_update = await get_user_by_id(user_id, db)
    if user_to_update and user_to_update.role != role_user:
        user_to_update.role = role_user
        db.commit()
        return True
    return None
