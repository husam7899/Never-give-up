from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum as SAEnum, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class OrderType(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"


class OrderStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DISPUTED = "disputed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentMethod(str, enum.Enum):
    TELEBIRR = "telebirr"
    CBE = "commercial_bank_of_ethiopia"
    DASHEN = "dashen_bank"
    AWASH = "awash_bank"
    ABYSSINIA = "abyssinia_bank"
    BOA = "bank_of_abyssinia"
    OTHER = "other_bank"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    order_type = Column(SAEnum(OrderType), nullable=False)
    status = Column(SAEnum(OrderStatus), default=OrderStatus.OPEN, nullable=False)
    usdt_amount = Column(Float, nullable=False)
    etb_amount = Column(Float, nullable=False)
    price_per_usdt = Column(Float, nullable=False)
    min_amount = Column(Float, nullable=True)
    max_amount = Column(Float, nullable=True)
    payment_method = Column(SAEnum(PaymentMethod), nullable=False)
    payment_details = Column(Text, nullable=True)
    chain = Column(String, nullable=False)
    taker_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    escrow_tx_hash = Column(String, nullable=True)
    escrow_released = Column(Boolean, default=False)

    creator = relationship("User", foreign_keys=[creator_id], lazy="joined")
    taker = relationship("User", foreign_keys=[taker_id], lazy="joined")

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)