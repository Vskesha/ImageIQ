from typing import Optional, List, Type

from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.security import HTTPBearer
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.conf import messages
from src.database.db import get_db
from src.database.models import Comment, User
from src.repository import comments as repository_comments, images as repository_images
from src.schemas.images import CommentModel, CommentResponse, SortDirection
from src.schemas.users import MessageResponse
from src.services.auth import auth_service
from src.services.role import allowed_all_roles_access, allowed_admin_moderator


router = APIRouter(prefix="/comment", tags=["comments"])
security = HTTPBearer()


@router.get(
    "/{comment_id}",
    description="Get a specific comment by its ID.\nNo more than 12 requests per minute.",
    dependencies=[
        Depends(allowed_all_roles_access),
        Depends(RateLimiter(times=12, seconds=60)),
    ],
    response_model=CommentResponse,
)
async def get_comment_by_id(
    comment_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.token_manager.get_current_user),
) -> Comment:
    """
    Get a specific comment by its ID.

    :param comment_id: int: ID of the comment to retrieve
    :param db: Session: Database session dependency
    :param current_user: User: Current user dependency
    :return: Comment: The retrieved comment
    """
    db_comment = await repository_comments.get_comment_by_id(comment_id, db)
    if db_comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )
    return db_comment


@router.get(
    "/image/{image_id}",
    description="Get all comments on image.\nNo more than 12 requests per minute.",
    dependencies=[
        Depends(allowed_all_roles_access),
        Depends(RateLimiter(times=12, seconds=60)),
    ],
    response_model=List[CommentResponse],
)
async def get_comments_by_image_id(
    image_id: int = Path(ge=1),
    sort_direction: SortDirection = SortDirection.desc,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.token_manager.get_current_user),
) -> List[Type[Comment]]:
    """
    The get_comments_by_image_id function returns a list of comments for the image with the given id.

    :param image_id: int: Get the comments of a specific image
    :param db: Session: Get the database session
    :param sort_direction: Sort the comments in ascending or descending order
    :param current_user: dict: Get the current user's information
    :return: The comments associated with the image
    """
    image = await repository_images.get_image(image_id, current_user, db)
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.MSC404_IMAGE_NOT_FOUND,
        )
    comments = await repository_comments.get_comments_by_image(image_id, sort_direction, db)
    return comments


@router.post(
    "/{image_id}",
    description="Add comment.\nNo more than 12 requests per minute.",
    dependencies=[
        Depends(allowed_all_roles_access),
        Depends(RateLimiter(times=12, seconds=60)),
    ],
    response_model=CommentResponse,
)
async def add_comment(
    body: CommentModel,
    image_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.token_manager.get_current_user),
) -> Optional[Comment]:
    """
    The add_comment function creates a new comment for an image.
    The function takes in the following parameters:
    body: CommentModel - A model containing the information of the comment to be created.
    image_id: int - The id of the image that will have a new comment added to it. This is passed as part of
    path parameter and must be greater than or equal to 1 (Path(ge=0)).

    :param body: CommentModel: Get the body of the comment
    :param image_id: int: Get the image_id from the url
    :param db: Session: Get the database session
    :param current_user: dict: Get the current user from the database
    :return: The created comment
    """
    image = await repository_images.get_image(image_id, current_user, db)
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.MSC404_IMAGE_NOT_FOUND,
        )
    comment = await repository_comments.add_comment(body, image_id, current_user, db)
    return comment


@router.patch(
    "/{comment_id}",
    description="Update comment.\nNo more than 12 requests per minute.",
    dependencies=[
        Depends(allowed_all_roles_access),
        Depends(RateLimiter(times=12, seconds=60)),
    ],
    response_model=CommentResponse,
)
async def update_comment(
    body: CommentModel,
    comment_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.token_manager.get_current_user),
) -> Comment:
    """
    The update_comment function updates a comment in the database.
    The function takes an id, body and current_user as parameters.
    It returns a Comment object if successful.

    :param body: CommentModel: Get the data from the request body
    :param comment_id: int: Get the comment id of the comment to be deleted
    :param db: Session: Get the database session
    :param current_user: dict: Get the user information from authuser
    :return: A comment object
    """
    comment = await repository_comments.update_comment(
        comment_id, body, current_user, db
    )
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.MSC404_COMMENT_NOT_FOUND,
        )

    return comment


@router.delete(
    "/{comment_id}",
    description="Delete comment.\nNo more than 12 requests per minute.",
    dependencies=[
        Depends(allowed_admin_moderator),
        Depends(RateLimiter(times=12, seconds=60)),
    ],
    response_model=MessageResponse,
)
async def remove_comment(
    comment_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.token_manager.get_current_user),
) -> dict:
    """
    The remove_comment function removes a comment from the database.
    The function takes in an integer representing the id of the comment to be removed,
    and returns a dictionary containing information about whether or not it was successful.

    :param comment_id: int: Get the comment id from the path
    :param db: Session: Pass the database session to the function
    :param current_user: dict: Get the current user information
    :return: A dict with the message key and value
    """
    message = await repository_comments.remove_comment(comment_id, current_user, db)

    return message
