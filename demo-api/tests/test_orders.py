from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.order import Order, OrderStatus


def _create_customer(client: TestClient, email: str = "alice@example.com") -> dict:
    response = client.post(
        "/api/customers",
        json={
            "name": "Alice Anderson",
            "email": email,
            "phone": "+1-555-0101",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_create_order(client: TestClient) -> None:
    customer = _create_customer(client)

    response = client.post(
        "/api/orders",
        json={
            "customer_id": customer["id"],
            "product_name": "Laptop",
            "amount": "1299.00",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["customer_id"] == customer["id"]
    assert body["product_name"] == "Laptop"
    assert body["amount"] == 1299.00
    assert body["status"] == "pending"
    assert "id" in body


def test_cancel_single_order(client: TestClient) -> None:
    customer = _create_customer(client)
    created = client.post(
        "/api/orders",
        json={
            "customer_id": customer["id"],
            "product_name": "Wireless Mouse",
            "amount": "29.90",
        },
    )
    order_id = created.json()["id"]

    response = client.post(f"/api/orders/{order_id}/cancel")

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"

    conflict = client.post(f"/api/orders/{order_id}/cancel")
    assert conflict.status_code == 409


def test_get_missing_order_returns_404(client: TestClient) -> None:
    response = client.get("/api/orders/99999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_cancel_all_cancels_active_orders(client: TestClient, db_session: Session) -> None:
    customer = Customer(name="Bob Brown", email="bob@example.com", phone="+1-555-0102")
    db_session.add(customer)
    db_session.flush()

    pending = Order(
        customer_id=customer.id,
        product_name="Keyboard",
        amount=Decimal("149.50"),
        status=OrderStatus.PENDING,
    )
    paid = Order(
        customer_id=customer.id,
        product_name="Monitor",
        amount=Decimal("399.00"),
        status=OrderStatus.PAID,
    )
    shipped = Order(
        customer_id=customer.id,
        product_name="Laptop Stand",
        amount=Decimal("45.00"),
        status=OrderStatus.SHIPPED,
    )
    already_cancelled = Order(
        customer_id=customer.id,
        product_name="USB Hub",
        amount=Decimal("19.99"),
        status=OrderStatus.CANCELLED,
    )
    refunded = Order(
        customer_id=customer.id,
        product_name="Headphones",
        amount=Decimal("89.99"),
        status=OrderStatus.REFUNDED,
    )
    db_session.add_all([pending, paid, shipped, already_cancelled, refunded])
    db_session.commit()

    response = client.post("/api/orders/cancel-all")

    assert response.status_code == 200
    body = response.json()
    assert body["cancelled_count"] == 3
    cancelled_ids = {order["id"] for order in body["orders"]}
    assert pending.id in cancelled_ids
    assert paid.id in cancelled_ids
    assert shipped.id in cancelled_ids
    assert already_cancelled.id not in cancelled_ids
    assert refunded.id not in cancelled_ids

    db_session.refresh(already_cancelled)
    db_session.refresh(refunded)
    assert already_cancelled.status == OrderStatus.CANCELLED
    assert refunded.status == OrderStatus.REFUNDED
