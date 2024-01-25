from typing import Optional, List

from fastapi import APIRouter, Depends, File, HTTPException, Path, status, UploadFile
from fastapi.security import HTTPBearer
from fastapi_limiter.depends import RateLimiter
from fastapi_pagination import Page, Params
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from src.conf import messages
from src.database.db import get_db
from src.database.models import Image, TransformationsType, User, Role
from src.repository import images as repository_images
from src.repository import tags as repository_tags
from src.schemas.images import ImageModel, ImageResponse, SortDirection
from src.schemas.users import MessageResponse
from src.services.auth import auth_service
from src.services.cloud_image import CloudImage
from src.services.role import allowed_all_roles_access, allowed_admin_moderator

router = APIRouter(prefix='/images', tags=['images'])
security = HTTPBearer()


@router.get("/all", response_model=Page[ImageResponse],
            description='Get images.\nNo more than 12 requests per minute.',
            dependencies=[
                          Depends(allowed_admin_moderator),
                          Depends(RateLimiter(times=12, seconds=60))
                          ],
            summary="Get all images if you are admin or moderator"
            )
async def get_images_all(
                 db: Session = Depends(get_db),
                 pagination_params: Params = Depends()
                    ) -> Page[ImageResponse]:


        """
        The get_images_all function returns a list of all images in the database.
        :param db: Session: Pass the database session to the repository layer
        :param pagination_params: Params: Get the pagination parameters from the request
        :return: A list of images
        """
        images = await repository_images.get_images_all(db, pagination_params)
        return images


@router.get("/by_user", response_model=Page[ImageResponse],
            description='Get images.\nNo more than 12 requests per minute.',
            dependencies=[
                          Depends(allowed_all_roles_access),
                          Depends(RateLimiter(times=12, seconds=60))
                          ],
            )
async def get_images_by_user(
                 db: Session = Depends(get_db),
                 current_user: User = Depends(auth_service.token_manager.get_current_user),
                 pagination_params: Params = Depends(),
                 sort_direction: SortDirection = SortDirection.desc
                    ) -> Page[ImageResponse]:


        """
        The get_images_by_user function returns a list of images that the current user has uploaded.
        The function takes in a pagination_params object, which is used to determine how many images are returned per page and what page number to return.
        :param db: Session: Access the database
        :param current_user: User: Get the current user from the database
        :param pagination_params: Params: Get the pagination parameters from the request
        :param sort_direction: SortDirection: Determine whether the images are sorted in ascending or descending order
        :return: A page object, which is a list of imageresponse objects
        """
        images = await repository_images.get_images_by_user(db, current_user, pagination_params, sort_direction)
        return images


@router.get('/{image_id}',
            description='Get image.\nNo more than 12 requests per minute',
            dependencies=[
                 Depends(allowed_all_roles_access),
                 Depends(RateLimiter(times=12, seconds=60))
            ],
            response_model=ImageResponse
            )
async def get_image(
                    image_id: int = Path(ge=1),
                    db: Session = Depends(get_db),
                    current_user: User = Depends(auth_service.token_manager.get_current_user),
                    ) -> Optional[Image]:
        """
        The get_image function is used to retrieve a single image from the database.
        The function takes in an image_id as a path parameter, and returns an Image object if it exists.
        If no such Image exists, then the function will return None.
        :param image_id: int: Get the image id from the path
        :param db: Session: Get the database session
        :param current_user: dict: Get the current user from the database
        :return: The image object
        """
        image = await repository_images.get_image(image_id, current_user, db)
        if image is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_IMAGE_NOT_FOUND)
        return image


@router.post('/transaction/{image_id}/{type}',
            description='Transform image.\nNo more than 12 requests per minute',
            dependencies=[
                 Depends(allowed_all_roles_access),
                 Depends(RateLimiter(times=12, seconds=60))
             ],
             response_model=ImageResponse
            )
async def transform_image(
                        type: TransformationsType,
                        image_id: int,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(auth_service.token_manager.get_current_user)
                    ):
    """
    The transform_image function is used to transform an image.
        The function takes in the following parameters:
            type (TransformationsType): The transformation type that will be applied to the image.
            image_id (int): The id of the image that will be transformed.

    :param type: TransformationsType: Specify the type of transformation that will be applied to the image
    :param image_id: int: Get the image from the database
    :param db: Session: Get the database session
    :param current_user: dict: Get the current user from the database
    :return: A new image with the transformation applied
    """
    image = await repository_images.get_image(image_id, current_user, db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_IMAGE_NOT_FOUND)
    if image.user_id != current_user.id and current_user.role != Role.admin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.MSC400_BAD_REQUEST)

    transform_image_link = CloudImage.transformation(image, type)
    body = {
        'description': image.description + ' ' + type.value,
        'link': transform_image_link,
        'tags': image.tags,
        'type': image.type
    }
    new_image = await repository_images.transform_image(body, image.user_id, db)
    return new_image


@router.get(''
            '/qrcode/{image_id}',
            description='No more than 12 requests per minute',
            dependencies=[
                           Depends(allowed_all_roles_access),
                           Depends(RateLimiter(times=12, seconds=60))
                           ]
            )
async def image_qry(
                    image_id: int = Path(ge=1),
                    db: Session = Depends(get_db),
                    current_user: User = Depends(auth_service.token_manager.get_current_user),
                    ):
        """
        The image_qry function is used to generate a QR code for the image.
        The QR code contains the URL of the image, which can be scanned by a mobile device.
        This function requires an authentication token and returns an HTTP response containing
        a PNG file with the QR code.
        :param image_id: int: Get the image id from the url
        :param db: Session: Get the database session
        :param current_user: dict: Get the current user from the token
        :return: A qr code image of the given image
        """
        image = await repository_images.get_image(image_id, current_user, db)
        if image is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_IMAGE_NOT_FOUND)
        qr_code = CloudImage.get_qrcode(image)
        return StreamingResponse(qr_code, media_type="image/png")


@router.post(
            '/',
            description='Create image.\nNo more than 2 requests per minute',
            dependencies=[
                Depends(allowed_all_roles_access),
                Depends(RateLimiter(times=2, seconds=60))
            ],
            response_model=ImageResponse
            )
async def create_image(
                        description: str = '-',
                        tags: str = '',
                        file: UploadFile = File(),
                        db: Session = Depends(get_db),
                        current_user: User = Depends(auth_service.token_manager.get_current_user),
                        ) -> Image:

        """
        The create_image function creates a new image in the database.
        :param description: str: Set the description of the image
        :param tags: str: Add tags to the image
        :param file: UploadFile: Get the file from the request
        :param db: Session: Get a database session
        :param current_user: dict: Get the current user
        :return: A new image
        """
        public_id = CloudImage.generate_name_image(current_user.email, file.filename)
        r = CloudImage.image_upload(file.file, public_id)
        src_url = CloudImage.get_url_for_image(public_id, r)
        body = {
            'description': description,
            'link': src_url,
            'tags': tags
        }
        image = await repository_images.create_image(body, current_user.id, db, 5)
        return image


@router.delete(
            '/{image_id}',
            description='Remove image.\nNo more than 12 requests per minute.',
            dependencies=[
                Depends(allowed_all_roles_access),
                Depends(RateLimiter(times=2, seconds=60))
            ],
            response_model=MessageResponse
               )
async def remove_image(
                    image_id: int = Path(ge=1),
                    db: Session = Depends(get_db),
                    current_user: User = Depends(auth_service.token_manager.get_current_user)
                    ) -> dict:

        """
        The remove_image function removes an image from the database.
        The function takes in an image_id and a database session, and returns a dictionary with a message.
        :param image_id: int: Get the image id from the path
        :param db: Session: Pass the database session to the repository
        :param current_user: dict: Get the current user from the database
        :return: A dictionary with a message
        """
        message = await repository_images.remove_image(image_id, current_user, db)
        if message is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_IMAGE_NOT_FOUND)
        return message


@router.patch(
            '/{image_id}',
            description='Update image.\nNo more than 12 requests per minute.',
            dependencies=[
                Depends(allowed_all_roles_access),
                Depends(RateLimiter(times=12, seconds=60))
            ],
            response_model=ImageResponse
            )
async def update_image(
                    body: ImageModel,
                    image_id: int = Path(ge=1),
                    db: Session = Depends(get_db),
                    current_user: User = Depends(auth_service.token_manager.get_current_user),
                    ) -> Image:
        """
        The update_image function updates an image in the database.
        The function takes a body of type ImageModel, which is defined in models/image.py, and an image_id of type int as parameters.
        The function also takes a db Session object from the get_db() dependency injection method, which is defined in crud/base.py;
        this allows us to access our database session for querying purposes (see https://docs.sqlalchemy.org/en/13/)
        :param body: ImageModel: Get the data from the request body
        :param image_id: int: Get the image id from the url
        :param db: Session: Get the database session
        :param current_user: dict: Get the current user
        :return: An image object
        """
        image = await repository_images.update_image(image_id, body, current_user, db, 5)
        if image is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_IMAGE_NOT_FOUND)
        return image


@router.get(
            '/search_bytag/{tag_name}',
            description='Get images by tag.\nNo more than 2 requests per minute.',
            dependencies=[
                          Depends(allowed_all_roles_access),
                          Depends(RateLimiter(times=2, seconds=60))
                          ],
            response_model=List[ImageResponse]
            )
async def get_image_by_tag_name(
                    tag_name: str,
                    sort_direction: SortDirection = SortDirection.desc,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(auth_service.token_manager.get_current_user),
            ) -> List[Image]:

        """
        The get_image_by_tag_name function returns a list of images that have the tag name specified in the request.
        The function takes three parameters:
        - tag_name: The name of the tag to search for. This is a required parameter and must be passed as part of
        the URL path (e.g., /images/tags/{tag_name}). It is also validated by FastAPI to ensure it meets
        certain criteria, such as being at least one character long and not exceeding 100 characters
        in length.
        :param tag_name: str: Get the tag from the database
        :param sort_direction: SortDirection: Specify the sort direction of the images
        :param db: Session: Pass the database session to the function
        :param current_user: dict: Get the current user from the token manager
        :return: A list of images
        """
        tag = await repository_tags.get_tag_by_name(tag_name, db)
        if tag is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_TAG_NOT_FOUND)

        images = await repository_images.get_images_by_tag(tag, sort_direction, db)
        if images is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_IMAGE_NOT_FOUND)

        return images


# @router.get(
#             '/search_byuser/{user_id}',
#             description='Get images by user_id.\nNo more than 2 requests per minute',
#             dependencies=[
#                           Depends(allowed_admin_moderator),
#                           Depends(RateLimiter(times=2, seconds=60))
#                           ],
#             response_model=List[ImageResponse]
#             )
# async def get_image_by_user(
#                             user_id: int,
#                             sort_direction: SortDirection,
#                             db: Session = Depends(get_db),
#                             current_user: User = Depends(auth_service.token_manager.get_current_user),
#                             credentials: HTTPAuthorizationCredentials = Security(security)
#                             ) -> List[Image]:
#
#         """
#         The get_image_by_user function returns a list of images that belong to the user with the given id.
#         The function takes in an integer representing the user's id, and a SortDirection enum value indicating whether
#         the returned list should be sorted by date ascending or descending. The function also takes in an
#         optional db Session object, a current_user dict containing information about the currently logged-in
#         user (if any), and credentials for HTTP Basic Authentication.
#
#         :param user_id: int: Get the user id from the url
#         :param sort_direction: SortDirection: Determine the order in which the images are returned
#         :param db: Session: Access the database
#         :param current_user: dict: Get the current user from the token
#         :return: A list of images
#         """
#         user = await repository_users.get_user_by_id(user_id, db)
#         if user is None:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_USER_NOT_FOUND)
#
#         images = await repository_images.get_images_by_user(user, sort_direction, db)
#         if not any(images):
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_IMAGE_NOT_FOUND)
#         return images



