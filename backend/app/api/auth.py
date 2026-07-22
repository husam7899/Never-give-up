from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.auth_service import register_user, login_user, login_telegram
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, UserResponse, TelegramAuthRequest

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register")
def register(data: UserRegister, db: Session = Depends(get_db)):
    try:
        result = register_user(db, data)
        user = db.query(User).filter(User.id == result["user_id"]).first()
        return {
            "access_token": result["access_token"],
            "token_type": "bearer",
            "user": UserResponse.model_validate(user),
        }
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    try:
        result = login_user(db, data)
        user = db.query(User).filter(User.id == result["user_id"]).first()
        return {
            "access_token": result["access_token"],
            "token_type": "bearer",
            "user": UserResponse.model_validate(user),
        }
    except ValueError as e:
        raise HTTPException(401, str(e))


@router.post("/telegram")
def telegram_auth(data: TelegramAuthRequest, db: Session = Depends(get_db)):
    try:
        result = login_telegram(db, data.init_data, data.email, data.username)
        user = db.query(User).filter(User.id == result["user_id"]).first()
        return {
            "access_token": result["access_token"],
            "token_type": "bearer",
            "user": UserResponse.model_validate(user),
        }
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.get("/profile/{user_id}")
def profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    return UserResponse.model_validate(user)