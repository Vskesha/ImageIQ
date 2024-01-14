import unittest
from unittest.mock import MagicMock
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.database.models import Comment, User
from src.repository.comments import (
    get_comments,
    get_comment_by_id,
    create_comment,
    update_comment,
    remove_comment,
)


class TestContactsRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.session = MagicMock(spec=Session)
        self.user = User(id=1, email="test@test.com")
        self.body = Comment(comment="some comment")
        self.image_id = 1
        self.comment_id = 1

    async def test_get_comments(self) -> None:
        # Mocking the query method of the session
        self.session.query().filter().all.return_value = [Comment(id=1, comment="comment 1")]
        result = await get_comments(self.session, self.image_id)
        self.assertEqual(result, [Comment(id=1, comment="comment 1")])

    async def test_get_comment_by_id(self) -> None:
        # Mocking the query method of the session
        self.session.query(Comment).get.return_value = Comment(id=1, comment="comment 1")
        result = await get_comment_by_id(self.session, self.comment_id)
        self.assertEqual(result, Comment(id=1, comment="comment 1"))

    async def test_create_comment(self) -> None:
        result = await create_comment(self.session, self.user, self.image_id, self.body)
        self.assertIsNotNone(result.id)
        self.assertEqual(result.comment, "some comment")
        self.assertEqual(result.user, self.user)
        self.assertEqual(result.image_id, self.image_id)

    async def test_update_comment_found(self) -> None:
        comment = Comment(id=1, comment="old comment", user=self.user, image_id=self.image_id)
        self.session.query(Comment).get.return_value = comment
        updated_comment = await update_comment(self.session, self.comment_id, self.body)
        self.assertEqual(updated_comment.comment, "some comment")
        self.assertNotEqual(updated_comment.updated_at, comment.updated_at)

    async def test_update_comment_not_found(self) -> None:
        self.session.query(Comment).get.return_value = None
        result = await update_comment(self.session, self.comment_id, self.body)
        self.assertIsNone(result)

    async def test_delete_comment_found(self) -> None:
        comment = Comment(id=1, comment="comment to delete", user=self.user, image_id=self.image_id)
        self.session.query(Comment).get.return_value = comment
        result = await remove_comment(self.session, self.comment_id)
        self.assertTrue(result)

    async def test_delete_comment_not_found(self) -> None:
        self.session.query(Comment).get.return_value = None
        result = await remove_comment(self.session, self.comment_id)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
