import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from src.database.models import Image, Tag, User
from src.schemas.images import ImageModel, SortDirection
from fastapi_pagination import Params,paginate
from unittest.mock import patch


from src.repository.images import (
    create_image,
    get_image,
    get_images_all,
    transform_image,
    remove_image,
    update_image,
    get_images_by_tag,
    get_images_by_user
)


class TestImagesRepository(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1, email="some@email.ua")

    @patch('fastapi_pagination.ext.sqlalchemy.paginate', wraps=paginate)
    async def test_get_images_all(self, mock_paginate):
        images = [Image(), Image()]
        self.session.query().filter().offset().limit().all.return_value = images
        pagination_params = Params(page=1, page_size=10)
        result = await get_images_all(db=self.session, pagination_params=pagination_params)
        self.session.query().filter().offset().limit().all.assert_called_once()
        mock_paginate.assert_called_once()
        self.assertEqual(result.items, images)


    async def test_create_image(self):
        image = ImageModel(name='Test image', description='Test description', tags=['test', 'image'])
        image_dict = image.__dict__
        result = await create_image(body=image_dict, user_id=self.user.id, db=self.session, tags_limit=5)
        self.assertTrue(hasattr(result, 'id'))
        self.assertEqual(result.description, image.description)
        self.assertEqual(result.user_id, self.user.id)
        self.assertEqual(result.tags, image.tags)

    async def test_get_image(self):
        image = Image()
        self.session.query().filter_by().first.return_value = image
        result = await get_image(image_id=image.id, user=self.user, db=self.session)
        self.assertEqual(image, result)

    async def test_transform_image(self):
        image = ImageModel(name='Test', description='Test tedt', tags=['test', 'image'])
        image_dict = image.__dict__
        self.session.query().filter_by().first.return_value = image
        result = await transform_image(body=image_dict, user_id=self.user.id, db=self.session)
        self.assertEqual(image, result)
    #
    async def test_remove_image(self):
        image = Image()
        self.session.query().filter_by().first.return_value = image
        result = await remove_image(image_id=image.id, user=self.user, db=self.session)
        self.assertEqual(image, result)
    #
    async def test_update_image(self):
        image = Image()
        self.session.query().filter_by().first.return_value = image
        result = await update_image(image_id=image.id, user=self.user, db=self.session)
        self.assertEqual(image, result)
    #
    async def test_get_images_by_tag(self):
        tag = Tag(name='test')
        sort_direction = SortDirection.asc
        expected_images = [Image(), Image()]
        self.session.query().filter_by().offset().limit().all.return_value = expected_images
        result = await get_images_by_tag(tag=tag, sort_direction=sort_direction, db=self.session)
        self.assertEqual(result, expected_images)
    #
    async def test_get_images_by_user(self):
        images = [Image(), Image()]
        user = self.user
        self.session.query().filter().offset().limit().all.return_value = images
        pagination_params = Params(page=1, page_size=10)
        result = await get_images_by_user(db=self.session, current_user=user, pagination_params=pagination_params)
        self.assertEqual(result.items, images)


if __name__ == '__main__':
    unittest.main()