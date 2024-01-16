import unittest
import asyncio
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from src.database.models import Comment, User
from src.schemas.images import CommentModel
from src.repository.comments import (
    add_comment,
    update_comment,
    remove_comment,
    get_comments,
    get_comment_by_id,
)
from src.conf import messages
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TestComments(unittest.TestCase):

    def setUp(self):
        self.db_session = MagicMock(spec=Session)
        self.user = User(id=1, username="testuser")
        self.db_session.add(self.user)
        self.db_session.commit()

    async def test_add_comment(self):
        comment_model = CommentModel(comment="Test Comment")
        added_comment = await add_comment(comment_model, image_id=1, user=self.user, db=self.db_session)

        self.assertIsNotNone(added_comment)
        self.assertEqual(added_comment.comment, "Test Comment")

    async def test_update_comment(self):
        comment_model = CommentModel(comment="Original Comment")
        added_comment = await add_comment(comment_model, image_id=1, user=self.user, db=self.db_session)

        updated_comment_model = CommentModel(comment="Updated Comment")
        updated_comment = await update_comment(
            comment_id=added_comment.id,
            body=updated_comment_model,
            user=self.user,
            db=self.db_session,
        )

        self.assertIsNotNone(updated_comment)
        self.assertEqual(updated_comment.comment, "Updated Comment")

    async def test_remove_comment(self):
        comment_model = CommentModel(comment="Test Comment")
        added_comment = await add_comment(comment_model, image_id=1, user=self.user, db=self.db_session)

        removed_comment = await remove_comment(
            comment_id=added_comment.id,
            user=self.user,
            db=self.db_session,
        )

        self.assertEqual(removed_comment, {"message": messages.COMMENT_DELETED})
        self.assertIsNone(self.db_session.query(Comment).get(added_comment.id))

    async def test_remove_comment_not_found(self):
        with self.assertRaises(HTTPException) as exc_info:
            await remove_comment(comment_id=999, user=self.user, db=self.db_session)

        self.assertEqual(exc_info.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(exc_info.exception.detail, messages.MSC404_COMMENT_NOT_FOUND)

    async def test_get_comments(self):
        comments = await get_comments(image_id=1, db=self.db_session)
        self.assertIsInstance(comments, list)

    async def test_get_comment_by_id(self):
        comment_model = CommentModel(comment="Test Comment")
        added_comment = await add_comment(comment_model, image_id=1, user=self.user, db=self.db_session)

        retrieved_comment = await get_comment_by_id(comment_id=added_comment.id, db=self.db_session)

        self.assertIsNotNone(retrieved_comment)
        self.assertEqual(retrieved_comment.id, added_comment.id)
        self.assertEqual(retrieved_comment.comment, added_comment.comment)


if __name__ == '__main__':
    asyncio.run(unittest.main(), debug=True)

