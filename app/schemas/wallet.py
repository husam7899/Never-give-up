from pydantic import BaseModel
from typing import Optional


class WalletCreate(BaseModel):
    chain: str
    address: str
    label: Optional[str] = None
    is_default: bool = False


class WalletResponse(BaseModel):
    id: int
    chain: str
    address: str
    label: Optional[str]
    is_default: bool

    model_config = {"from_attributes": True}