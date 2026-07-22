from pydantic import BaseModel, Field
from typing import Optional, List


class OrderCreate(BaseModel):
    order_type: str
    usdt_amount: float = Field(..., gt=0)
    price_per_usdt: float = Field(..., gt=0)
    payment_method: str
    chain: str
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    payment_details: Optional[str] = None


class OrderResponse(BaseModel):
    id: int
    creator_id: int
    creator_username: Optional[str] = None
    order_type: str
    status: str
    usdt_amount: float
    etb_amount: float
    price_per_usdt: float
    min_amount: Optional[float]
    max_amount: Optional[float]
    payment_method: str
    chain: str
    taker_id: Optional[int] = None
    created_at: str
    creator_total_trades: int = 0
    creator_completion_rate: float = 100.0
    creator_rating: float = 0.0

    model_config = {"from_attributes": True}


class OrderListResponse(BaseModel):
    orders: List[OrderResponse]
    total: int
    page: int
    page_size: int