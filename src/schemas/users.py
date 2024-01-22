from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from src.database.models import Role


class UserModel(BaseModel):
    username: str = Field(min_length=1, max_length=25)
    email: EmailStr
    password: str = Field(min_length=4, max_length=15)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    avatar: str
    role: Role

    model_config = ConfigDict(from_attributes = True)


class ProfileResponse(UserResponse):
    created_at: datetime
    comments_count: int
    images_count: int


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr


class MessageResponse(BaseModel):
    message: str = Field(max_length=2000)


class UpdateProfile(BaseModel):
    username: str | None = Field(min_length=2, max_length=16)


class UpdateFullProfile(UpdateProfile):
    username: Optional[str]
    email: EmailStr | str


class ChangeRoleModel(BaseModel):
    user_id: int
    user_role: Role


class ResponseBanned(BaseModel):
    message: str = Field(max_length=2000)
