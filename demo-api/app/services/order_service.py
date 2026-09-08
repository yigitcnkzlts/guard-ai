from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.customer import Customer
from app.models.order import Order, OrderStatus
from app.schemas.order import OrderCreate

ACTIVE_STATUSES = (OrderStatus.PENDING, OrderStatus.PAID, OrderStatus.SHIPPED)
CANCELLABLE_STATUSES = ACTIVE_STATUSES
REFUNDABLE_STATUSES = (OrderStatus.PAID, OrderStatus.SHIPPED)


def _touch(order: Order) -> None:
    order.updated_at = datetime.now(timezone.utc)


def create_order(db: Session, payload: OrderCreate) -> Order:
    customer = db.get(Customer, payload.customer_id)
    if customer is None:
        raise NotFoundError(f"Customer {payload.customer_id} not found")

    order = Order(
        customer_id=payload.customer_id,
        product_name=payload.product_name,
        amount=payload.amount,
        status=OrderStatus.PENDING,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def list_orders(db: Session) -> list[Order]:
    return db.query(Order).order_by(Order.id.asc()).all()


def get_order(db: Session, order_id: int) -> Order:
    order = db.get(Order, order_id)
    if order is None:
        raise NotFoundError(f"Order {order_id} not found")
    return order


def cancel_order(db: Session, order_id: int) -> Order:
    order = get_order(db, order_id)

    if order.status == OrderStatus.CANCELLED:
        raise ConflictError("Order is already cancelled")
    if order.status not in CANCELLABLE_STATUSES:
        raise ConflictError(f"Order with status '{order.status.value}' cannot be cancelled")

    order.status = OrderStatus.CANCELLED
    _touch(order)
    db.commit()
    db.refresh(order)
    return order


def refund_order(db: Session, order_id: int) -> Order:
    order = get_order(db, order_id)

    if order.status == OrderStatus.REFUNDED:
        raise ConflictError("Order is already refunded")
    if order.status not in REFUNDABLE_STATUSES:
        raise ConflictError(f"Order with status '{order.status.value}' cannot be refunded")

    order.status = OrderStatus.REFUNDED
    _touch(order)
    db.commit()
    db.refresh(order)
    return order


def cancel_all_active_orders(db: Session) -> list[Order]:
    # This endpoint intentionally represents a dangerous bulk action for GUARD AI security testing.
    orders = (
        db.query(Order)
        .filter(Order.status.in_(ACTIVE_STATUSES))
        .order_by(Order.id.asc())
        .all()
    )
    for order in orders:
        order.status = OrderStatus.CANCELLED
        _touch(order)

    db.commit()
    for order in orders:
        db.refresh(order)
    return orders
