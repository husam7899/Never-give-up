from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import DEMO_MODE
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
    order_type: str = "BUY",
    payment_method: str = None,
    chain: str = None,
    db: Session = Depends(get_db),
):
    try:
        orders = list_orders(db, page, page_size, order_type, payment_method, chain)
        if DEMO_MODE and (not orders or len(orders) == 0):
            # Return rich mock orders in DEMO mode if DB is empty
            return [
                {
                    "id": 101,
                    "creator_id": 1,
                    "creator_username": "AddisTrader",
                    "order_type": order_type.upper(),
                    "status": "ACTIVE",
                    "usdt_amount": 1000.0,
                    "etb_amount": 142500.0,
                    "price_per_usdt": 142.50,
                    "min_amount": 1000.0,
                    "max_amount": 50000.0,
                    "payment_method": "TELEBIRR",
                    "chain": "BEP20",
                    "created_at": "2026-07-22T00:00:00",
                    "creator_total_trades": 142,
                    "creator_completion_rate": 99.1,
                    "creator_rating": 4.9
                },
                {
                    "id": 102,
                    "creator_id": 2,
                    "creator_username": "EthioCryptoPro",
                    "order_type": order_type.upper(),
                    "status": "ACTIVE",
                    "usdt_amount": 500.0,
                    "etb_amount": 71000.0,
                    "price_per_usdt": 142.00,
                    "min_amount": 2000.0,
                    "max_amount": 30000.0,
                    "payment_method": "CBE",
                    "chain": "TRC20",
                    "created_at": "2026-07-22T01:00:00",
                    "creator_total_trades": 89,
                    "creator_completion_rate": 98.5,
                    "creator_rating": 4.8
                }
            ]
        return orders
    except Exception as e:
        if DEMO_MODE:
            return [
                {
                    "id": 101,
                    "creator_id": 1,
                    "creator_username": "AddisTrader",
                    "order_type": order_type.upper(),
                    "status": "ACTIVE",
                    "usdt_amount": 1000.0,
                    "etb_amount": 142500.0,
                    "price_per_usdt": 142.50,
                    "min_amount": 1000.0,
                    "max_amount": 50000.0,
                    "payment_method": "TELEBIRR",
                    "chain": "BEP20",
                    "created_at": "2026-07-22T00:00:00",
                    "creator_total_trades": 142,
                    "creator_completion_rate": 99.1,
                    "creator_rating": 4.9
                }
            ]
        raise HTTPException(500, str(e))


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