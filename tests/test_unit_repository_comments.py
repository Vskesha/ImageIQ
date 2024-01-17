import unittest
import asyncio
from asynctest import patch, TestCase, MagicMock
from unittest.mock import MagicMock, call
from tests.conftest import TestingSessionLocal
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from src.database.models import Comment, User, Image
from src.schemas.images import CommentModel
from src.repository.comments import (
    add_comment,
    update_comment,
    remove_comment,
    get_comments,
    get_comment_by_id,
    get_comments_by_image
)
from src.conf import messages
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class AsyncTestComments(TestCase):
    async def setUp(self):
        self.mock_session = MagicMock()
        self.mock_session.add = MagicMock()
        self.mock_session.commit = MagicMock()
        self.user = User(id=1, username="testuser")  

    @patch('tests.conftest.TestingSessionLocal', new_callable=MagicMock)
    async def test_your_async_function(self, mock_session):
        mock_session.return_value = self.mock_session

    async def asyncTearDown(self):
        await super().asyncTearDown()
        self.mock_session.close.assert_awaited_once()

    async def test_add_comment(self):
        comment_model = CommentModel(comment="Test Comment")
        added_comment = await add_comment(comment_model, image_id=1, user=self.user, db=self.mock_session)
        self.assertIsNotNone(added_comment)
        self.assertEqual(added_comment.comment, "Test Comment")

    async def test_update_comment(self):
        comment_model = CommentModel(comment="Original Comment")
        added_comment = await add_comment(comment_model, image_id=1, user=self.user, db=self.mock_session)

        updated_comment_model = CommentModel(comment="Updated Comment")
        updated_comment = await update_comment(
        comment_id=added_comment.id,
        body=updated_comment_model,
        user=self.user,
        db=self.mock_session,
        )
        self.assertIsNotNone(updated_comment)
        self.assertEqual(updated_comment.comment, "Updated Comment")

    async def test_remove_comment(self):
        comment_model = CommentModel(comment="Test Comment")
        added_comment = await add_comment(comment_model, image_id=1, user=self.user, db=self.mock_session)
        result = await remove_comment(comment_id=added_comment.id, user=self.user, db=self.mock_session)
        self.assertEqual(result, {"message": messages.COMMENT_DELETED})

    
    async def test_remove_comment_not_found(self):
        with self.assertRaises(HTTPException) as exc_info:
            await remove_comment(comment_id=999, user=self.user, db=self.mock_session)
        print(f"Exception: {exc_info.exception}")
        self.assertEqual(exc_info.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(exc_info.exception.detail, messages.MSC404_COMMENT_NOT_FOUND)



    async def test_get_comments_by_image_found(self):
        image_id = 1
        mock_image = MagicMock()
        mock_comment1 = Comment(id=1, image_id=image_id, comment="Comment 1")
        mock_comment2 = Comment(id=2, image_id=image_id, comment="Comment 2")

        self.mock_session.query.return_value.filter_by.return_value.first.return_value = mock_image
        self.mock_session.query.return_value.filter_by.return_value.all.return_value = [mock_comment1, mock_comment2]

        result = await get_comments_by_image(image_id, self.mock_session)

        self.assertEqual(result, [mock_comment1, mock_comment2])
        self.assertEqual(result[0].id, 1)
        self.assertEqual(result[0].image_id, image_id)
        self.assertEqual(result[0].comment, "Comment 1")

        self.assertEqual(result[1].id, 2)
        self.assertEqual(result[1].image_id, image_id)
        self.assertEqual(result[1].comment, "Comment 2")

        
    async def test_get_comments_by_image_not_found(self):
        image_id = 1
        self.mock_session.query.return_value.filter_by.return_value.first.return_value = None
        
        result = await get_comments_by_image(image_id, self.mock_session)

        self.mock_session.query.assert_called_once_with(Image)
        self.mock_session.query.return_value.filter_by.assert_called_once_with(id=image_id)
        self.mock_session.query.return_value.filter_by.return_value.first.assert_called_once()
        self.mock_session.query.return_value.filter_by.return_value.all.assert_not_called()
        self.assertEqual(result, {"detail": "Image not found"})

    async def test_get_comment_by_id(self):
        comment_model = CommentModel(comment="Test Comment")
        added_comment = await add_comment(comment_model, image_id=1, user=self.user, db=self.mock_session)
        comment_id = added_comment.id

        mock_query = self.mock_session.query.return_value.filter_by.return_value
        mock_query.first.return_value = added_comment   

        retrieved_comment = await get_comment_by_id(comment_id=comment_id, db=self.mock_session)
        self.assertIsInstance(retrieved_comment, Comment)
        self.assertEqual(retrieved_comment, added_comment)
        self.assertEqual(retrieved_comment.id, added_comment.id)
        self.assertEqual(retrieved_comment.comment, added_comment.comment)


    async def test_get_comments(self):
        image_id = 1
        mock_query = self.mock_session.query.return_value.filter_by.return_value
        mock_query.all.return_value = []   

        comments = await get_comments(image_id=image_id, db=self.mock_session)
        self.assertIsInstance(comments, list)
        self.assertEqual(comments, [])   



if __name__ == '__main__':
    asyncio.run(unittest.main(), debug=True)

