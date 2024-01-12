from fastapi import  HTTPException, Depends, status, APIRouter
from sqlalchemy.orm import Session
from src.database.models import Comment, User, Role
from src.database.db import get_db
from fastapi.security import  HTTPBearer
from src.services.auth import get_current_user

router = APIRouter(prefix='/comments', tags=['comments'])
security = HTTPBearer()
 



def get_comment(db: Session, comment_id: int):
    return db.query(Comment).filter(Comment.id == comment_id).first()

@router.post("/users/", response_model=User)
async def create_user(username: str, email: str, password: str, role: str = "user", db: Session = Depends(get_db)):
    user = User(username=username, email=email, password=password, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/comments/", response_model=Comment)
async def add_comment(comment: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_comment = Comment(comment=comment, user_id=current_user.id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.get("/comments", response_model=list[Comment])
async def get_comments_by_image_id(image_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    comments = db.query(Comment).filter(Comment.image_id == image_id).all()
    return comments

@router.put("/comments/{comment_id}", response_model=Comment)
async def update_comment(comment_id: int, comment: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_comment = get_comment(db, comment_id)
    if db_comment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    db_comment.comment = comment
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.delete("/comments/{comment_id}", response_model=Comment)
async def remove_comment(comment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_comment = get_comment(db, comment_id)
    allowed_roles = {Role.admin, Role.moderator}
    if current_user.role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    db.delete(db_comment)
    db.commit()
    return db_comment

