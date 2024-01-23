from typing import List, Type

from fastapi import APIRouter, Depends, Path, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.conf import messages
from src.database.db import get_db
from src.database.models import Rating, User
from src.schemas.images import RatingResponse, RatingModel, AverageRatingResponse
from src.schemas.users import MessageResponse
from src.services.auth import auth_service
from src.services.role import allowed_all_roles_access, allowed_admin_moderator

from src.repository import images as repository_images, ratings as repository_ratings

router = APIRouter(prefix="/ratings", tags=["ratings"])
security = HTTPBearer()


@router.get(
    "/{image_id}/all",
    description=f"Get all ratings for image.\nNo more than 12 requests per minute.",
    dependencies=[
        Depends(allowed_admin_moderator),
        Depends(RateLimiter(times=12, seconds=60)),
    ],
    response_model=List[RatingResponse],
)
async def get_all_ratings(
    image_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.token_manager.get_current_user),
) -> List[Type[Rating]]:
    """
    The get_all_ratings function returns a list of all ratings for the image with the given ID.
    :param image_id: int: Specify the id of the image to get all ratings for
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the user that is currently logged in
    :param : Get the image id from the url path
    :return: A list of rating objects
    """
    image = await repository_images.get_image(image_id, current_user, db)
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.IMAGE_NOT_FOUND
        )

    ratings = await repository_ratings.get_ratings(image_id, db)

    return ratings


@router.get(
    "/{image_id}",
    description=f"Get average rating of image.\nNo more than 12 requests per minute.",
    dependencies=[
        Depends(allowed_all_roles_access),
        Depends(RateLimiter(times=12, seconds=60)),
    ],
    response_model=AverageRatingResponse
)
async def get_rating(
    image_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.token_manager.get_current_user),
) -> AverageRatingResponse:
    """
    The get_rating function returns the average rating of an image.
    :param image_id: int: Get the image id from the url path
    :param db: Session: Pass the database session to the repository function
    :param current_user: User: Get the user who is making the request
    :param : Get the image id from the url
    :return: An average rating response object
    """
    image = await repository_images.get_image(image_id, current_user, db)
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.IMAGE_NOT_FOUND
        )

    average_rating = await repository_ratings.get_average_rating(image_id, db)

    return AverageRatingResponse(rating=average_rating)


@router.post(
    "/{image_id}",
    description=f"Add rating.\nCan rate for an image only once.",
    dependencies=[
        Depends(allowed_all_roles_access),
        Depends(RateLimiter(times=12, seconds=60)),
    ],
    response_model=RatingResponse,
)
async def add_rating(
    body: RatingModel,
    image_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.token_manager.get_current_user),
) -> Rating:
    """
    The add_rating function creates a new rating for an image.
    :param body: RatingModel: Get the rating value from the request body
    :param image_id: int: Get the id of the image that is being rated
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the user who is currently logged in
    :param : Get the image id from the path
    :return: A rating object
    """
    image = await repository_images.get_image(image_id, current_user, db)

    if image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.IMAGE_NOT_FOUND
        )

    existing_rating = (
        db.query(Rating)
        .filter(Rating.image_id == image_id, Rating.user_id == current_user.id)
        .first()
    )

    if existing_rating:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=messages.RATING_ALREADY_EXISTS,
        )

    if image.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=messages.CANNOT_RATE_OWN_IMAGE,
        )

    rating = await repository_ratings.add_rating(body, image_id, current_user, db)
    return rating


@router.delete(
    "/{rating_id}",
    description=f"Delete rating.\nNo more than 12 requests per minute.",
    dependencies=[
        Depends(allowed_admin_moderator),
        Depends(RateLimiter(times=12, seconds=60)),
    ],
    response_model=MessageResponse,
)
async def remove_rating(
    rating_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.token_manager.get_current_user),
) -> dict:
    """
    The remove_rating function removes a rating from the database.
    The function takes in an integer representing the id of the rating to be removed,
    and returns a dictionary containing a message indicating that the removal was successful.
    :param rating_id: int: Get the id of the rating that will be removed
    :param db: Session: Get the database session
    :param current_user: User: Get the user id of the current user
    :param : Get the rating id from the url
    :return: A dictionary with a message key and value
    """
    rating = await repository_ratings.get_rating(rating_id, db, current_user)

    if rating is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.RATING_NOT_FOUND
        )

    await repository_ratings.remove_rating(rating_id, db, current_user)

    return {"message": messages.RATING_REMOVED}
