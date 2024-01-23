from typing import List, Type

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.conf import messages
from src.database.models import Rating, Image, User, Role
from src.schemas.images import RatingModel


async def add_rating(
    body: RatingModel, image_id: int, user: User, db: Session
) -> Rating:
    """
    The add_rating function adds a rating to an image.
    
    :param body: RatingModel: Get the rating from the request body
    :param image_id: int: Get the image that is being rated
    :param user: User: Get the user id of the current user
    :param db: Session: Access the database
    :return: A rating object
    """
    # Check if the image exists
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.IMAGE_NOT_FOUND
        )

    # Check if the user is not the owner of the image
    if image.user_id == user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=messages.CANNOT_RATE_OWN_IMAGE
        )

    # Check if the user has already rated the image
    existing_rating = (
        db.query(Rating)
        .filter(Rating.image_id == image_id, Rating.user_id == user.id)
        .first()
    )
    if existing_rating:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=messages.ALREADY_RATED
        )

    # Create a new rating
    rating = Rating(image_id=image_id, user_id=user.id, rating=body.rating)
    db.add(rating)
    db.commit()
    db.refresh(rating)

    return rating


async def get_rating(rating_id: int, db: Session, user: User) -> Type[Rating]:
    """
    The get_rating function is used to retrieve a rating from the database.
        It checks if the user is an admin or moderator, and if not it raises a 403 error.
        If the user is an admin or moderator, it then checks if the rating exists in 
        our database and returns that rating object.
    
    :param rating_id: int: Get the rating by id
    :param db: Session: Access the database
    :param user: User: Check if the user is an admin or moderator
    :return: A type[rating] object
    """
    # Check if the user is admin or moderator
    if user.role != Role.admin and user.role != Role.moderator:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=messages.NOT_ALLOWED
        )
    # Check if the rating exists
    rating = db.query(Rating).filter(Rating.id == rating_id).first()
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.RATING_NOT_FOUND
        )

    return rating


async def get_ratings(image_id: int, db: Session) -> List[Type[Rating]]:
    """
    The get_ratings function returns all ratings for a given image.
    
    :param image_id: int: Specify the image id that is passed in from the url
    :param db: Session: Pass the database session to the function
    :return: A list of ratings for the image
    """
    # Check if the image exists
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.IMAGE_NOT_FOUND
        )

    # Get all ratings for the image
    ratings = db.query(Rating).filter(Rating.image_id == image_id).all()

    return ratings


async def get_average_rating(image_id: int, db: Session) -> float:
    """
    The get_average_rating function returns the average rating of an image.
        Args:
            image_id (int): The id of the image to get ratings for.
            db (Session): A database session object used to query the database.
        Returns:
            float: The average rating rounded to 2 decimal places.
    
    :param image_id: int: Get the image id from the database
    :param db: Session: Pass the database session to the function
    :return: The average rating of an image
    """
    average_rating = (
        db.query(func.avg(Rating.rating)).filter_by(image_id=image_id).scalar()
    )
    if not average_rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.RATING_NOT_FOUND
        )
    return round(average_rating, 2)


async def remove_rating(rating_id: int, db: Session, user: User) -> dict:
    """
    The remove_rating function removes a rating from the database.
        Args:
            rating_id (int): The id of the rating to be removed.
            db (Session): A connection to the database.
            user (User): The user making this request, used for authorization purposes.
    
    :param rating_id: int: Specify the id of the rating to be deleted
    :param db: Session: Access the database
    :param user: User: Check if the user is admin or moderator
    :return: A dict, but the function expects a rating
    """
    # Check if the rating exists
    rating = db.query(Rating).filter(Rating.id == rating_id).first()
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.RATING_NOT_FOUND
        )

    # Check if the user is moderator or admin
    if user.role != Role.admin and user.role != Role.moderator:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=messages.NOT_AUTHORIZED
        )

    # Delete the rating
    db.delete(rating)
    db.commit()

    return {"message": messages.RATING_DELETED}
