from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token


def register_user(db: Session, data) -> dict:
    existing = db.query(User).filter(
        (User.email == data.email) | (User.username == data.username)
    ).first()
    if existing:
        raise ValueError("Email or username already registered")

    user = User(
        email=data.email,
        username=data.username,
        hashed_password=hash_password(data.password),
        phone=data.phone,
        full_name=data.full_name,
        telegram_id=data.telegram_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "user_id": user.id}


def login_user(db: Session, data) -> dict:
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise ValueError("Invalid username or password")

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "user_id": user.id}


def login_telegram(db: Session, telegram_id: str, email: str = None, username: str = None) -> dict:
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        if not email:
            email = f"tg_{telegram_id}@p2p.app"
        if not username:
            username = f"tg_{telegram_id[:8]}"
        user = User(
            telegram_id=telegram_id,
            email=email,
            username=username,
            hashed_password=hash_password(telegram_id + "_secret"),
            is_verified=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "user_id": user.id}