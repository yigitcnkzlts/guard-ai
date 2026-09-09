from app.core.config import settings
from app.database.base import Base
from app.database.session import SessionLocal, engine
from app.services.bootstrap import (
    seed_customer_support_agent,
    seed_developer_agent,
    seed_finance_agent,
)


def bootstrap_database() -> None:
    """Create and seed the disposable demo database when configured."""
    if not settings.should_bootstrap_database:
        return

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_customer_support_agent(db)
        seed_finance_agent(db)
        seed_developer_agent(db)
