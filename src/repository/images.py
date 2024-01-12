from typing import Optional, List, Type

from fastapi import HTTPException, status
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from src.database.models import Image, Tag
from src.schemas.images import ImageModel
from src.conf import messages
from src.repository import tags as repository_tags
from src.database.models import User
from src.schemas.images import ImageModel, ImageResponse, SortDirection

async def get_images_all(
        db: Session,
        pagination_params: Params
        ) -> Page[ImageResponse]:

    """
    The get_images_all function returns a list of all images in the database.

    :param db: Session: Pass the database session to the function
    :param pagination_params: Params: Pass the pagination parameters to the function
    :return: A page of images
    :doc-author: Trelent
    """
    query = db.query(Image)
    images = paginate(query, params=pagination_params)
    return images


async def get_images_by_user(
        db: Session,
        current_user: User,
        pagination_params: Params
        ) -> Page[ImageResponse]:

    """
    The get_images_by_user function returns a list of images that belong to the current user.

    :param db: Session: Get access to the database
    :param current_user: User: Pass the current user into the function
    :param pagination_params: Params: Specify the pagination parameters
    :return: A page object, which is a
    :doc-author: Trelent
    """
    query = db.query(Image).filter(Image.user == current_user)
    images = paginate(query, params=pagination_params)
    return images

async def get_image(
    image_id: int,
    user: User,
    db: Session,
) -> Optional[Image]:
    """
    The get_image function takes in an image_id, a user, and a database session.
    It returns the Image object with the given id if it exists.

    :param image_id: int: Specify the image id that is being requested
    :param user: dict: Pass the user's information to the function
    :param db: Session: Access the database
    :param : Get the image id from the database
    :return: The image with the given id
    :doc-author: Trelent
    """
    return db.query(Image).filter_by(id=image_id).first()


async def create_image(
    body: dict,
    user_id: int,
    db: Session,
    tags_limit: int
) -> Image | Exception:

    """
    The create_image function creates a new image in the database.
        Args:
            body (dict): The request body containing the image's description, link and tags.
            user_id (int): The id of the user who created this image.
            db (Session): A connection to our database session object.

    :param body:dict: Get the data from the request body
    :param user_id: int: Get the user id from the token
    :param db: Session: Pass the database session to the function
    :param tags_limit: int: Limit the number of tags that can be added to an image
    :return: A new image object
    :doc-author: Trelent
    """
    tags_names = body['tags'].split()
    if len(tags_names) > tags_limit:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT_BAD_REQUEST,
            detail=messages.MSC409_TAGS
        )

    tags = []
    for el in tags_names:
        tag = await repository_tags.get_tag_by_name(el, db)
        if tag is None:
            tag = await repository_tags.create_tag(el, db)
        tags.append(tag)
    try:
        image = Image(description=body['description'], link=body['link'], user_id=user_id, tags=tags)
    except Exception as er:
        return er

    db.add(image)
    db.commit()
    db.refresh(image)
    return image


async def transform_image(
        body: dict,
        user_id: int,
        db: Session
) -> Image:
    """
    The transform_image function takes in a dictionary of image data, the user_id of the user who created it, and a database session.
    It then creates an Image object from that data and adds it to the database. It returns either an error or the newly created Image.

    :param body: dict: Get the data from the request body
    :param user_id: int: Make sure that the image is created by the user who is logged in
    :param db: Session: Access the database
    :return: An image object
    :doc-author: Trelent
    """
    try:
        image = Image(
            description=body['description'],
            link=body['link'],
            user_id=user_id,
            type=body['type'],
            tags=body['tags']
        )
    except Exception as er:
        return er

    db.add(image)
    db.commit()
    db.refresh(image)
    return image


async def remove_image(
        image_id: int,
        user: User,
        db: Session
) -> dict:
    """
    The remove_image function is used to remove an image from the database.
        The function takes in three arguments:
            - image_id: the id of the image to be removed, as an integer.
            - user: a dictionary containing information about the user making this request, including their role and id.
                    This is used for authorization purposes (only admins and moderators can delete images that are not theirs).
                    If a non-admin/moderator tries to delete another user's images, they will receive a 403 Forbidden error message.

    :param image_id: int: Identify the image to be deleted
    :param user: dict: Check if the user is an admin or moderator
    :param db: Session: Access the database
    :return: A dict with a message saying that the image has been deleted
    :doc-author: Trelent
    """
    if user.role in ['admin', 'moderator']:
        image: Optional[Image] = db.query(Image).filter_by(id=image_id).first()
    else:
        image: Optional[Image] = db.query(Image).filter_by(id=image_id, user_id=user.id).first()
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_IMAGE_NOT_FOUND)
    else:
        db.delete(image)
        db.commit()
    return {'message': messages.DELETED_IMAGE}


async def update_image(
        image_id: int,
        body: ImageModel,
        user: User,
        db: Session,
        tags_limit: int
) -> Optional[Image]:
    """
    The update_image function updates an image in the database.
        Args:
            image_id (int): The id of the image to update.
            body (ImageModel): The updated information for the Image object.
            user (dict): A dictionary containing a user's role and id, used to determine if they have permission to update this Image object.  If not, None is returned instead of an updated Image object.

    :param image_id: int: Get the image by id
    :param body: ImageModel: Pass the data from the request body to the function
    :param user: dict: Check if the user is an admin or moderator,
    :param db: Session: Pass the database session to the function
    :param tags_limit: int: Limit the number of tags that can be added to an image
    :return: The updated image
    :doc-author: Trelent
    """
    if user.role in ['admin', 'moderator']:
        image: Optional[Image] = db.query(Image).filter_by(id=image_id).first()
    else:
        image: Optional[Image] = db.query(Image).filter_by(id=image_id, user_id=user.id).first()

    if not image or not body.description:
        return None

    image.description = body.description

    tags_names = body.tags.split()[:tags_limit]
    tags = []
    for el in tags_names:
        tag = await repository_tags.get_tag_by_name(el, db)
        if tag is None:
            tag = await repository_tags.create_tag(el, db)
        tags.append(tag)

    image.tags = tags
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


# async def get_images_by_tag(tag: Tag, sort_direction: SortDirection, db: Session) -> List[Image]:
#     """
#     The get_images_by_tag function takes in a tag and a sort direction,
#     then returns all images associated with that tag.
#
#     :param tag: Filter the images by tag
#     :param sort_direction: Determine whether the images are sorted in ascending or descending order
#     :param db: Pass the database connection to the function
#     :return: A list of images, sorted by the created_at field in ascending or descending order
#     :doc-author: Trelent
#     """
#     image_tag = db.query(ImageM2MTag).filter_by(tag_id=tag.id).all()
#     images_id = [el.image_id for el in image_tag]
#     order_by_field = desc(Image.created_at) if sort_direction == SortDirection.desc else asc(Image.created_at)
#     images = db.query(Image).filter(Image.id.in_(images_id)).order_by(order_by_field).all()
#     if not images:
#         print(f"No images found for tag '{tag.name}' with sort direction '{sort_direction.value}'")
#         return []


# async def get_images_by_user(user_id, sort_direction, db):
#     """
#     The get_images_by_user function returns a list of images that are associated with the user_id provided.
#     The sort_direction parameter is used to determine whether the results should be sorted in ascending or descending order.
#
#     :param user_id: Filter the images by user
#     :param sort_direction: Determine whether the images should be sorted in ascending or descending order
#     :param db: Pass the database connection to the function
#     :return: A list of image objects that are associated with a user
#     :doc-author: Trelent
#     """
#     if sort_direction.value == 'desc':
#         images = db.query(Image).filter_by(user_id=user_id).order_by(desc(Image.created_at)).all()
#     else:
#         images = db.query(Image).filter_by(user_id=user_id).order_by(asc(Image.created_at)).all()
#     return images
