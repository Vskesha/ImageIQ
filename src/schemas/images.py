import enum
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional

from src.database.models import TransformationsType


class TagModel(BaseModel):
    name: str = Field(max_length=20)

    class Config:
        orm_mode = True


class ImageModel(BaseModel):
    description: str = Field(max_length=50)
    tags: str
    rating: Optional[float] = None


class ImageResponse(ImageModel):
    id: int
    link: str
    user_id: int
    created_at: datetime
    updated_at: datetime
    tags: List[TagModel]
    rating: Optional[float] = None

    class Config:
        orm_mode = True


class TransformateModel(BaseModel):
    Type: TransformationsType


class SortDirection(enum.Enum):
    asc = 'asc'
    desc = 'desc'


class CommentModel(BaseModel):
    comment: str = Field(max_length=2000)


class CommentResponse(CommentModel):
    id: int
    comment: str = Field(max_length=2000)
    user_id: int
    created_at: datetime
    updated_at: datetime
    image_link: str

    class Config:
        orm_mode = True


class RatingModel(BaseModel):
    rating: Optional[float] = Field(ge=1, le=5)


class AverageRatingResponse(RatingModel):
    rating: Optional[float] = Field(ge=1, le=5)


class RatingResponse(RatingModel):
    id: int
    rating: Optional[float] = Field(ge=1, le=5)
    user_id: int = 1
    image_id: int = 1
    created_at: datetime

    class Config:
        orm_mode = True