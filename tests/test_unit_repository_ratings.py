import unittest
import sys
sys.path.insert(0, '')

from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock
from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from src.conf import messages
from src.database.models import Rating, Image, User, Role
from src.schemas.images import RatingModel
from src.repository.ratings import(
    add_rating,
    get_rating,
    get_ratings,
    get_average_rating,
    remove_rating
)

class TestRatings(IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        self.image = Image(id=1)
        
    async def test_add_rating(self):
        body = RatingModel(rating=5)
        with self.assertRaises(HTTPException) as context:
            await add_rating(body, 1, self.user, self.session)

        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(context.exception.detail, messages.IMAGE_NOT_FOUND)

    async def test_get_rating(self):
        with self.assertRaises(HTTPException) as context:
            await get_rating(1, self.session, self.user)

        self.assertEqual(context.exception.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(context.exception.detail, messages.NOT_ALLOWED)

    async def test_get_ratings(self):
        with self.assertRaises(HTTPException) as context:
            await get_ratings(1, self.session)

        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(context.exception.detail, messages.IMAGE_NOT_FOUND)

    async def test_get_average_rating(self):
        with self.assertRaises(HTTPException) as context:
            await get_average_rating(1, self.session)

        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(context.exception.detail, "Rating not found.")

    async def test_remove_rating(self):
        with self.assertRaises(HTTPException) as context:
            await remove_rating(1, self.session, self.user)

        self.assertEqual(context.exception.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(context.exception.detail, messages.NOT_AUTHORIZED)

if __name__ == '__main__':
    unittest.main()
