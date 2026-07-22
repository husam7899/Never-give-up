from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.transaction import Transaction, TxStatus
from app.models.order import Order, OrderStatus
from app.models.user import User
from app.models.transaction import Dispute
from fastapi import HTTPException


def get_user_transactions(db: Session, user_id: int) -> list:
    return (
        db.query(Transaction)
        .filter((Transaction.seller_id == user_id) | (Transaction.buyer_id == user_id))
        .order_by(Transaction.created_at.desc())
        .all()
    )


def initiate_escrow(db: Session, user_id: int, transaction_id: int, tx_hash: str):
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(404, "Transaction not found")
    if tx.seller_id != user_id:
        raise HTTPException(403, "Only seller can initiate escrow")
    tx.tx_hash = tx_hash
    tx.tx_status = TxStatus.PENDING
    order = db.query(Order).filter(Order.id == tx.order_id).first()
    if order:
        order.escrow_tx_hash = tx_hash
    db.commit()
    return tx


def confirm_payment(db: Session, user_id: int, transaction_id: int, payment_ref: str):
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(404, "Transaction not found")
    if tx.buyer_id != user_id:
        raise HTTPException(403, "Only buyer can confirm payment")
    tx.payment_ref = payment_ref
    tx.payment_confirmed = True
    db.commit()
    return tx


def release_escrow(db: Session, user_id: int, transaction_id: int):
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(404, "Transaction not found")
    if tx.buyer_id != user_id:
        raise HTTPException(403, "Only buyer can release escrow")
    tx.tx_status = TxStatus.CONFIRMED
    tx.completed_at = datetime.now(timezone.utc)
    order = db.query(Order).filter(Order.id == tx.order_id).first()
    if order:
        order.status = OrderStatus.COMPLETED
        order.escrow_released = True
        order.completed_at = datetime.now(timezone.utc)
        for uid in [order.creator_id, order.taker_id]:
            user = db.query(User).filter(User.id == uid).first()
            if user:
                user.total_trades += 1
    db.commit()
    return tx


def raise_dispute(db: Session, user_id: int, transaction_id: int, reason: str, description: str = None):
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(404, "Transaction not found")
    dispute = Dispute(
        transaction_id=transaction_id,
        raised_by=user_id,
        reason=reason,
        description=description,
    )
    db.add(dispute)
    order = db.query(Order).filter(Order.id == tx.order_id).first()
    if order:
        order.status = OrderStatus.DISPUTED
    db.commit()
    return dispute