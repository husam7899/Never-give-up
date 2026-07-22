from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.order_service import create_order, list_orders, accept_order, cancel_order, get_user_orders

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("")
def create(data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        order = create_order(db, current_user.id, data)
        return {
            "id": order.id,
            "creator_id": order.creator_id,
            "creator_username": current_user.username,
            "order_type": order.order_type.value,
            "status": order.status.value,
            "usdt_amount": order.usdt_amount,
            "etb_amount": order.etb_amount,
            "price_per_usdt": order.price_per_usdt,
            "min_amount": order.min_amount,
            "max_amount": order.max_amount,
            "payment_method": order.payment_method.value,
            "chain": order.chain,
            "created_at": order.created_at.isoformat() if order.created_at else "",
            "creator_total_trades": current_user.total_trades,
            "creator_completion_rate": current_user.completion_rate,
            "creator_rating": current_user.rating,
        }
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("")
def list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    order_type: str = None,
    payment_method: str = None,
    chain: str = None,
    db: Session = Depends(get_db),
):
    return list_orders(db, page, page_size, order_type, payment_method, chain)


@router.post("/accept")
def accept(data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        accept_order(db, current_user.id, data["order_id"])
        return {"message": "Order accepted"}
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/cancel")
def cancel(data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        cancel_order(db, current_user.id, data["order_id"])
        return {"message": "Order cancelled"}
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/my")
def my_orders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    orders = get_user_orders(db, current_user.id)
    result = []
    for o in orders:
        result.append({
            "id": o.id,
            "creator_id": o.creator_id,
            "creator_username": o.creator.username if o.creator else None,
            "order_type": o.order_type.value,
            "status": o.status.value,
            "usdt_amount": o.usdt_amount,
            "etb_amount": o.etb_amount,
            "price_per_usdt": o.price_per_usdt,
            "payment_method": o.payment_method.value,
            "chain": o.chain,
            "taker_id": o.taker_id,
            "created_at": o.created_at.isoformat() if o.created_at else "",
        })
    return {"orders": result}