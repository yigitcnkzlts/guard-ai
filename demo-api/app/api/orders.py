from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.order import CancelAllResponse, OrderCreate, OrderRead
from app.services import order_service

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderRead, status_code=201)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)) -> OrderRead:
    return order_service.create_order(db, payload)


@router.get("", response_model=list[OrderRead])
def list_orders(db: Session = Depends(get_db)) -> list[OrderRead]:
    return order_service.list_orders(db)


@router.post("/cancel-all", response_model=CancelAllResponse)
def cancel_all_orders(db: Session = Depends(get_db)) -> CancelAllResponse:
    """This endpoint intentionally represents a dangerous bulk action for GUARD AI security testing."""
    # This endpoint intentionally represents a dangerous bulk action for GUARD AI security testing.
    orders = order_service.cancel_all_active_orders(db)
    return CancelAllResponse(cancelled_count=len(orders), orders=orders)


@router.get("/{order_id}", response_model=OrderRead)
def get_order(order_id: int, db: Session = Depends(get_db)) -> OrderRead:
    return order_service.get_order(db, order_id)


@router.post("/{order_id}/cancel", response_model=OrderRead)
def cancel_order(order_id: int, db: Session = Depends(get_db)) -> OrderRead:
    return order_service.cancel_order(db, order_id)


@router.post("/{order_id}/refund", response_model=OrderRead)
def refund_order(order_id: int, db: Session = Depends(get_db)) -> OrderRead:
    return order_service.refund_order(db, order_id)
