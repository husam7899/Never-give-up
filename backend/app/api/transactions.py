from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.transaction_service import (
    get_user_transactions, initiate_escrow, confirm_payment,
    release_escrow, raise_dispute
)

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.get("")
def list_transactions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    txs = get_user_transactions(db, current_user.id)
    return {"transactions": [
        {
            "id": tx.id,
            "order_id": tx.order_id,
            "seller_id": tx.seller_id,
            "buyer_id": tx.buyer_id,
            "chain": tx.chain,
            "tx_hash": tx.tx_hash,
            "usdt_amount": tx.usdt_amount,
            "etb_amount": tx.etb_amount,
            "payment_method": tx.payment_method,
            "payment_ref": tx.payment_ref,
            "payment_confirmed": tx.payment_confirmed,
            "tx_status": tx.tx_status.value if tx.tx_status else "pending",
            "platform_fee_usdt": tx.platform_fee_usdt,
            "platform_fee_etb": tx.platform_fee_etb,
            "created_at": tx.created_at.isoformat() if tx.created_at else "",
            "completed_at": tx.completed_at.isoformat() if tx.completed_at else None,
        }
        for tx in txs
    ]}


@router.post("/escrow")
def escrow(data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        tx = initiate_escrow(db, current_user.id, data["transaction_id"], data["tx_hash"])
        return {"message": "Escrow initiated", "tx_hash": tx.tx_hash}
    except HTTPException as e:
        raise e


@router.post("/confirm-payment")
def confirm(data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        tx = confirm_payment(db, current_user.id, data["transaction_id"], data["payment_ref"])
        return {"message": "Payment confirmed"}
    except HTTPException as e:
        raise e


@router.post("/release")
def release(data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        release_escrow(db, current_user.id, data["transaction_id"])
        return {"message": "USDT released to seller"}
    except HTTPException as e:
        raise e


@router.post("/dispute")
def dispute(data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        d = raise_dispute(db, current_user.id, data["transaction_id"], data["reason"], data.get("description"))
        return {"message": "Dispute raised", "dispute_id": d.id}
    except HTTPException as e:
        raise e