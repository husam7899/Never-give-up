from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum as SAEnum, ForeignKey, Text
from datetime import datetime, timezone
import enum
from app.core.database import Base

class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    role = Column(SAEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    total_trades = Column(Integer, default=0)
    completion_rate = Column(Float, default=100.0)
    rating = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class UserWallet(Base):
    __tablename__ = "user_wallets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    chain = Column(String, nullable=False)
    address = Column(String, nullable=False)
    label = Column(String, nullable=True)
    is_default = Column(Boolean, default=False)
