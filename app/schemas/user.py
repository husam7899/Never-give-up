from pydantic import BaseModel
from typing import Optional


class UserRegister(BaseModel):
    email: str
    username: str
    password: str
    phone: Optional[str] = None
    full_name: Optional[str] = None
    telegram_id: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    telegram_id: Optional[str] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    is_verified: bool
    total_trades: int
    completion_rate: float
    rating: float
    created_at: str

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TelegramAuthRequest(BaseModel):
    init_data: str
    email: Optional[str] = None
    username: Optional[str] = None