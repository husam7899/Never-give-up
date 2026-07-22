from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.order import Order, OrderType, OrderStatus, PaymentMethod
from app.models.user import User
from app.models.transaction import Transaction


def create_order(db: Session, user_id: int, data) -> Order:
    order = Order(
        creator_id=user_id,
        order_type=OrderType(data.order_type),
        usdt_amount=data.usdt_amount,
        etb_amount=round(data.usdt_amount * data.price_per_usdt, 2),
        price_per_usdt=data.price_per_usdt,
        payment_method=PaymentMethod(data.payment_method),
        chain=data.chain.upper(),
        min_amount=data.min_amount or data.usdt_amount * 0.1,
        max_amount=data.max_amount or data.usdt_amount,
        payment_details=data.payment_details,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def list_orders(db: Session, page=1, page_size=20, order_type=None, payment_method=None, chain=None):
    query = db.query(Order).filter(Order.status == OrderStatus.OPEN)
    if order_type:
        query = query.filter(Order.order_type == OrderType(order_type))
    if payment_method:
        query = query.filter(Order.payment_method == PaymentMethod(payment_method))
    if chain:
        query = query.filter(Order.chain == chain.upper())
    query = query.order_by(Order.created_at.desc())

    total = query.count()
    orders = query.offset((page - 1) * page_size).limit(page_size).all()

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
            "min_amount": o.min_amount,
            "max_amount": o.max_amount,
            "payment_method": o.payment_method.value,
            "chain": o.chain,
            "taker_id": o.taker_id,
            "created_at": o.created_at.isoformat() if o.created_at else "",
            "creator_total_trades": o.creator.total_trades if o.creator else 0,
            "creator_completion_rate": o.creator.completion_rate if o.creator else 100.0,
            "creator_rating": o.creator.rating if o.creator else 0.0,
        })
    return {"orders": result, "total": total, "page": page, "page_size": page_size}


def accept_order(db: Session, user_id: int, order_id: int) -> Order:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise ValueError("Order not found")
    if order.status != OrderStatus.OPEN:
        raise ValueError("Order already taken")
    if order.creator_id == user_id:
        raise ValueError("Cannot accept your own order")

    order.status = OrderStatus.IN_PROGRESS
    order.taker_id = user_id

    tx = Transaction(
        order_id=order.id,
        seller_id=order.creator_id if order.order_type == OrderType.SELL else user_id,
        buyer_id=user_id if order.order_type == OrderType.SELL else order.creator_id,
        chain=order.chain,
        usdt_amount=order.usdt_amount,
        etb_amount=order.etb_amount,
        payment_method=order.payment_method.value,
        platform_fee_usdt=round(order.usdt_amount * 0.005, 2),
        platform_fee_etb=round(order.etb_amount * 0.005, 2),
    )
    db.add(tx)
    db.commit()
    return order


def cancel_order(db: Session, user_id: int, order_id: int):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise ValueError("Order not found")
    if order.creator_id != user_id:
        raise ValueError("Only creator can cancel")
    if order.status != OrderStatus.OPEN:
        raise ValueError("Only open orders can be cancelled")
    order.status = OrderStatus.CANCELLED
    db.commit()


def get_user_orders(db: Session, user_id: int) -> list:
    return (
        db.query(Order)
        .filter(or_(Order.creator_id == user_id, Order.taker_id == user_id))
        .order_by(Order.created_at.desc())
        .all()
    )