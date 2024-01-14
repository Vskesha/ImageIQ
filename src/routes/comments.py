from fastapi import  HTTPException, Depends, status, APIRouter
from sqlalchemy.orm import Session
from src.database.models import Comment, User, Role, Image
from src.database.db import get_db
from fastapi.security import  HTTPBearer
from src.services.auth import auth_service
from src.repository.comments import get_comment

router = APIRouter(prefix='/comments', tags=['comments'])
security = HTTPBearer()
 
get_current_user = auth_service.token_manager.get_current_user



@router.post("/comments/", response_model=Comment)
async def add_comment(image_id: int, comment: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
     
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

     
    db_comment = Comment(comment=comment, user_id=current_user.id, image_id=image_id)
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