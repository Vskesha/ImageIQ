import pickle
from typing import Optional, List, Type

from fastapi import HTTPException, status
from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.conf import messages
from src.database.models import User
from src.schemas.users import UserModel
from src.services.auth import auth_service


async def get_cache_user_by_email(email: str, cache = None) -> User | None:
    """
    The get_cache_user_by_email function is used to retrieve a user from the cache.
        Args:
            email (str): The email of the user to be retrieved.
            cache (Redis): A Redis connection object, if not provided will use default global connection.

    :param email: str: Specify the email of the user to be retrieved from cache
    :param cache: Pass in the redis cache object
    :return: A user object or none
    """
    if email:
        user_bytes = None
        try:
            if cache:
                user_bytes = await cache.get(f"user:{email}")
            if user_bytes is None:
                return None
            user = pickle.loads(user_bytes)  # type: ignore
            print(f"Get from Redis  {str(user.email)}")
        except Exception as err:
            print(f"Error Redis read {err}")
            user = None
        return user


async def update_cache_user(user: User, cache = None):
    """
    The update_cache_user function takes a user object and an optional cache object.
    If the cache is provided, it will save the user to Redis with a key of &quot;user:&lt;email&gt;&quot;.
    The value will be pickled so that we can store arbitrary Python objects in Redis.
    We also set an expiration time of 900 seconds (15 minutes) on this key.
    :param user: User: Pass in the user object
    :param cache: Pass in the cache object
    :return: A coroutine, which is a special object that can be used with await or yield from
    """
    if user and cache:
        email = user.email
        try:
            await cache.set(f"user:{email}", pickle.dumps(user))
            await cache.expire(f"user:{email}", 900)
            print(f"Save to Redis {str(user.email)}")
        except Exception as err:
            print(f"Error redis save, {err}")


async def get_user_by_email(email: str, db: Session) -> User | None:
    """
    The get_user_by_email function takes in an email and a database session,
    and returns the user with that email if it exists. If no such user exists,
    it returns None.
    :param email: str: Specify the email of the user we want to retrieve from our database
    :param db: Session: Pass the database session to the function
    :return: The first user that matches the email
    """
    return db.query(User).filter_by(email=email).first()


async def get_user_by_id(user_id: int, db: Session) -> Optional[User]:
    """
    The get_user_by_id function returns a user object from the database, given an id.
    :param user_id: int: Specify the type of data that is expected to be passed into the function
    :param db: Session: Pass in the database session that is created in the main
    :return: The first user in the database with a matching id
    :doc-author: Trelent
    """
    return db.query(User).filter(User.id == user_id).first()


async def create_user(body: UserModel, db: Session):
    """
    The create_user function creates a new user in the database.

    :param body: UserModel: Get the data from the request body
    :param db: Session: Pass the database session to the function
    :return: A user object, which is a sqlalchemy model
    """
    g = Gravatar(body.email)
    new_user = User(**body.dict(), avatar=g.get_image())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    The update_token function updates the refresh token for a user.
    Args:
    user (UserModel): The UserModel object to update.
    refresh_token (str): The new refresh token to use for this user.
    db (Session): A database session object used to commit changes.
    :param user: UserModel: Pass in the user object that is returned from the get_user function
    :param token: Update the refresh_token in the database
    :param db: Session: Access the database
    :return: The user object
    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    The confirmed_email function takes in an email and a database session,
    and sets the confirmed field of the user with that email to True.


    :param email: str: Specify the email address of the user
    :param db: Session: Pass in the database session
    :return: None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    """
    The update_avatar function updates the avatar of a user.

    :param email: Find the user in the database
    :param url: str: Specify the type of data that will be passed into the function
    :param db: Session: Pass the database session to the function
    :return: The user with the updated avatar
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user


async def ban_user(user_id: int, active_status: bool, db: Session) -> Type[User] | None:
    """
    The ban_user function is used to ban a user from the site.
    The function takes in an email and a database session, and returns
    the user that was banned.
    """
    user = db.query(User).filter_by(id=user_id).first()

    # Print user values before commit
    # print(f"User values before commit: {user.id}, {user.username}, {user.email}, {user.status_active}")

    if not user:
        return None

    if user.role.value == 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=messages.NOT_ALLOWED)

    user.status_active = active_status
    db.commit()
    db.refresh(user)
    return user


async def change_password_for_user(user: User, password: str, db: Session) -> User:
    user.password = password
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


async def get_all_users(db: Session) -> List[User]:
    """
    The get_all_users function returns a list of all users in the database.

    :param db: Session: Pass the database session to the function
    :return: A list of users
    :doc-author: Trelent
    """
    users = db.query(User).all()
    users = [await get_user_by_id(user.id, db) for user in users]
    return users


def clear_user_cache(user: User) -> None:
    """_summary_

    :param user: Clear user from cached storage
    :type user: User
    """
    auth_service.token_manager.r.delete(f"user:{user.email}")


async def get_user_by_username(
        username: str, db: Session,
        status_active: bool | None = True) -> User | None:
    """
    Retrieves a user by his username.

    :param username: An username to get user from the database by.
    :type username: str
    :param db: The database session.
    :type db: Session
    :return: The user.
    :rtype: User
    """
    user = db.query(User).filter(User.username == username).first()
    return user
