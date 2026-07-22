from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum as SAEnum, ForeignKey, Text
from app.core.database import Base
import enum


class TxStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    chain = Column(String, nullable=False)
    tx_hash = Column(String, nullable=True, index=True)
    from_address = Column(String, nullable=True)
    to_address = Column(String, nullable=True)
    usdt_amount = Column(Float, nullable=False)
    tx_status = Column(SAEnum(TxStatus), default=TxStatus.PENDING)
    etb_amount = Column(Float, nullable=False)
    payment_method = Column(String, nullable=True)
    payment_ref = Column(String, nullable=True)
    payment_confirmed = Column(Boolean, default=False)
    platform_fee_usdt = Column(Float, default=0.0)
    platform_fee_etb = Column(Float, default=0.0)
    dispute_reason = Column(Text, nullable=True)
    dispute_resolved_by = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)


class Dispute(Base):
    __tablename__ = "disputes"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False, index=True)
    raised_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    reason = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="open", nullable=False)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolution_note = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime(timezone=True), nullable=True)