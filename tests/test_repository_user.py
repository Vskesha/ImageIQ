from datetime import datetime
from fastapi import HTTPException
import unittest
import pickle
import pytest
from unittest.mock import MagicMock, AsyncMock,patch
from pydantic import EmailStr
from sqlalchemy.orm import Session
from src.schemas.users import UserModel
from src.services.auth import auth_service
from src.database.models import Role, User
from src.repository.users import (
    get_user_by_email,
    get_user_by_id,
    create_user,
    update_token,
    confirmed_email,
    update_avatar,
    change_password_for_user,
    get_user_by_username
)

import aioredis
class TestUsers(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = AsyncMock(spec=Session)
        self.user_admin = User(
            id=1,
            username='Admin',
            email='Unknown1@mail.com',
            password='Qwerty@123',
            created_at=datetime.now(),
            updated_at=datetime.now(),
            avatar='default',
            refresh_token='eyJhb...-iV1MI',
            role=Role.user,
            confirmed=True,
            status_active=True
        )
        self.user = User(
            id=2,
            username='User',
            email='Asdsdown1@mail.com',
            password='Qwerty@123',
            created_at=datetime.now(),
            updated_at=datetime.now(),
            avatar='default',
            refresh_token='eyJhb...-iV1MI',
            role=Role.admin,
            confirmed=True,
            status_active=True
        )
    async def test_get_user_by_email_found(self):
        self.session.query().filter_by().first.return_value = self.user_admin
        result = await get_user_by_email(self.user_admin.email, self.session)
        self.assertIsInstance(result, User)
        self.assertEqual(result.email, self.user_admin.email)

    async def test_get_user_by_email_not_found(self):
        self.session.query().filter_by().first.return_value = None
        result = await get_user_by_email('nonexistent@mail.com', self.session)
        self.assertIsNone(result)

    async def test_get_user_by_id_found(self):
        self.session.query(User).filter(User.id == self.user.id).first.return_value = self.user
        result = await get_user_by_id(self.user.id, self.session)
        self.assertIsInstance(result, User)
        self.assertEqual(result.id, self.user.id)


    async def test_get_user_admin_by_id_found(self):
        self.session.query(User).filter(User.id == self.user.id).first.return_value = self.user_admin
        result = await get_user_by_id(self.user_admin.id, self.session)
        self.assertIsInstance(result, User)
        self.assertEqual(result.id, self.user_admin.id)

    async def test_get_user_by_id_not_found(self):
        self.session.query(User).filter(User.id == self.user.id).first.return_value = None
        result = await get_user_by_id(999, self.session)
        self.assertIsNone(result)


    async def test_get_user_admin_id_not_found(self):
        self.session.query(User).filter(User.id == self.user_admin.id).first.return_value = None
        result = await get_user_by_id(99, self.session)
        self.assertIsNone(result)

    async def test_create_user_first_success(self):
        # Test creating the first user as an admin
        self.session.query().count.return_value = 0
        result = await create_user(UserModel(username='Admin', email=self.user_admin.email, password=self.user_admin.password), self.session)
        self.assertIsInstance(result, User)
        self.assertEqual(result.role, Role.admin)

    async def test_create_user_not_first_success(self):
        # Test creating a regular user when there are existing users
        self.session.query().count.return_value = 1
        result = await create_user(UserModel(username='User', email=self.user.email, password=self.user.password),
                                   self.session)
        self.assertIsInstance(result, User)
        self.assertEqual(result.role, Role.user)

    async def test_change_password_for_user_success(self):
        # Test changing password for a user successfully
        result = await change_password_for_user(self.user, 'NewPassword123', self.session)
        self.assertEqual(result.password, 'NewPassword123')

    async def test_update_token_success(self):
        await update_token(self.user, 'new_refresh_token', self.session)
        self.assertEqual(self.user.refresh_token, 'new_refresh_token')

    async def test_update_token_fail(self):
        self.session.query().filter_by().first.return_value = None
        result = await update_token(User(), 'new_refresh_token', self.session)
        self.assertIsNone(result)

    async def test_confirmed_email_success(self):
        await confirmed_email(self.user.email, self.session)
        self.assertTrue(self.user.confirmed)

    async def test_update_avatar_success(self):
        self.session.query().filter_by().first.return_value = self.user
        result = await update_avatar(self.user.email, 'new_avatar_url', self.session)
        self.assertEqual(result.avatar, 'new_avatar_url')

    async def test_get_user_by_username_success(self):
        self.session.query().filter().first.return_value = self.user_admin
        result = await get_user_by_username('Admin', self.session)
        self.assertIsInstance(result, User)
        self.assertEqual(result.username, 'Admin')



if __name__ == '__main__':
    unittest.main()