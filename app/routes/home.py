from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.models import User
from app.database import get_db
from app.security import get_current_user

router = APIRouter(
    tags=["home"]
)


@router.post("/home")
async def post_username(current_user: User = Depends(get_current_user)):
    return {
        "username": current_user.username
    }

# Getting user's info for chatbot username greeting function
@router.get("/user")
def get_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == current_user.id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email
    }
