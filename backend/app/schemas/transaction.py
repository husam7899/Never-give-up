from pydantic import BaseModel
from typing import Optional, List


class TransactionResponse(BaseModel):
    id: int
    order_id: int
    seller_id: int
    buyer_id: int
    chain: str
    tx_hash: Optional[str]
    usdt_amount: float
    etb_amount: float
    payment_method: Optional[str]
    payment_ref: Optional[str]
    payment_confirmed: bool
    tx_status: str
    platform_fee_usdt: float
    platform_fee_etb: float
    created_at: str
    completed_at: Optional[str]

    model_config = {"from_attributes": True}


class TransactionListResponse(BaseModel):
    transactions: List[TransactionResponse]
    total: int