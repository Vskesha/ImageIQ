import enum
from datetime import date
from typing import List

from sqlalchemy import (String, Integer, ForeignKey, DateTime, func, Enum, Boolean,
                        Float, CheckConstraint, UniqueConstraint, select)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.database.db import SessionLocal

session = SessionLocal()


class Base(DeclarativeBase):
    pass


class Role(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[date] = mapped_column("created_at", DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column(
        "updated_at", DateTime, default=func.now(), onupdate=func.now()
    )
    role: Mapped[Enum] = mapped_column(
        "role", Enum(Role), default=Role.admin, nullable=True
    )
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    status_active: Mapped[bool] = mapped_column(Boolean, default=True)


class TransformationsType(enum.Enum):
    basic: str = 'basic'
    avatar: str = 'avatar'
    black_white: str = 'black_white'
    delete_bg: str = 'delete_bg'
    cartoonify: str = 'cartoonify'
    oil_paint: str = 'oil_paint'
    sepia: str = 'sepia'
    vector: str = 'vector'
    outline: str = 'outline'


class ImageM2MTag(Base):
    __tablename__ = 'image_m2m_tag'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    image_id: Mapped[int] = mapped_column(Integer, ForeignKey('images.id', ondelete='CASCADE'))
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey('tags.id', ondelete='CASCADE'))


class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)


class Image(Base):
    __tablename__ = 'images'
    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    type: Mapped[TransformationsType] = mapped_column(Enum(TransformationsType), default=TransformationsType.basic)
    link: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    user: Mapped[User] = relationship("User", backref='images')
    tags: Mapped[List[Tag]] = relationship("Tag", secondary="image_m2m_tag", backref='images')
    created_at: Mapped[date] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    @hybrid_property
    def rating(self):
        try:
            avg_rating = (session.query(func.avg(Rating.rating))
                          .filter(Rating.image_id == self.id)
                          .group_by(Rating.image_id).scalar())
            return avg_rating or 0.0
        except Exception:
            return 0.0


class Comment(Base):
    __tablename__ = 'comments'
    id: Mapped[int] = mapped_column(primary_key=True)
    comment: Mapped[str] = mapped_column(String(2000))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    user: Mapped[User] = relationship("User", backref='comments')
    image_id: Mapped[int] = mapped_column(Integer, ForeignKey('images.id', ondelete='CASCADE'), nullable=True)
    image: Mapped[Image] = relationship("Image", backref='comments')
    created_at: Mapped[date] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Rating(Base):
    __tablename__ = 'ratings'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    user: Mapped[User] = relationship("User", backref='ratings')
    image_id: Mapped[int] = mapped_column(Integer, ForeignKey('images.id', ondelete='CASCADE'), nullable=True)
    image: Mapped[Image] = relationship("Image", backref='ratings')
    rating: Mapped[float] = mapped_column(Float, CheckConstraint('rating >= 1 AND rating <= 5'))
    created_at: Mapped[date] = mapped_column(DateTime, default=func.now())

    __table_args__ = (
        UniqueConstraint('user_id', 'image_id', name='_user_image_uc'),)
