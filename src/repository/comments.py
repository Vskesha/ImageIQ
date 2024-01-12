from sqlalchemy.orm import Session
from src.database.models import Comment, User, Role

from datetime import datetime


def get_comment(db: Session, comment_id: int):
    return db.query(Comment).filter(Comment.id == comment_id).first()


async def get_comments(session: Session, image_id: int):
    return session.query(Comment).filter(Comment.image_id == image_id).all()


async def get_comment_by_id(session: Session, comment_id: int):
    return session.query(Comment).get(comment_id)


async def create_comment(session: Session, user: User, image_id: int, comment_body: Comment):
    comment = Comment(
        comment=comment_body.comment,
        user=user,
        image_id=image_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment


async def update_comment(session: Session, user: User, comment_id: int, comment_body: Comment):
    comment = session.query(Comment).get(comment_id)
    if comment and Comment.user == user:
        Comment.comment = comment_body.comment
        Comment.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(comment)
        return comment


async def remove_comment(session: Session, user: User, comment_id: int):
    comment = session.query(Comment).get(comment_id)
    if comment:
        # Check if the user is an admin or moderator before allowing deletion
        if Role.moderator or Role.admin:
            session.delete(comment)
            session.commit()
            return True
    return False
