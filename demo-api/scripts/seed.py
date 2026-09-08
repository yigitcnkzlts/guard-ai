from decimal import Decimal

from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.models.customer import Customer
from app.models.order import Order, OrderStatus


def seed(db: Session) -> None:
    if db.query(Customer).first() is not None:
        print("Database already seeded, skipping.")
        return

    alice = Customer(name="Alice Anderson", email="alice@example.com", phone="+1-555-0101")
    bob = Customer(name="Bob Brown", email="bob@example.com", phone="+1-555-0102")
    carol = Customer(name="Carol Clark", email="carol@example.com", phone="+1-555-0103")
    db.add_all([alice, bob, carol])
    db.flush()

    db.add_all(
        [
            Order(
                customer_id=alice.id,
                product_name="Laptop",
                amount=Decimal("1299.00"),
                status=OrderStatus.PENDING,
            ),
            Order(
                customer_id=alice.id,
                product_name="Wireless Mouse",
                amount=Decimal("29.90"),
                status=OrderStatus.PAID,
            ),
            Order(
                customer_id=bob.id,
                product_name="Mechanical Keyboard",
                amount=Decimal("149.50"),
                status=OrderStatus.SHIPPED,
            ),
            Order(
                customer_id=bob.id,
                product_name="Monitor",
                amount=Decimal("399.00"),
                status=OrderStatus.CANCELLED,
            ),
            Order(
                customer_id=carol.id,
                product_name="Headphones",
                amount=Decimal("89.99"),
                status=OrderStatus.REFUNDED,
            ),
            Order(
                customer_id=carol.id,
                product_name="Webcam",
                amount=Decimal("59.00"),
                status=OrderStatus.PENDING,
            ),
        ]
    )
    db.commit()
    print("Seed data created: 3 customers, 6 orders.")


def main() -> None:
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
