import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("DEMOSHOP_BASE_URL", "http://demo-api:8000")
os.environ.setdefault("UPSTREAM_TIMEOUT_SECONDS", "5")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000")

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.models import Agent, Policy, SecurityEvent  # noqa: F401
from app.services.bootstrap import seed_customer_support_agent

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        seed_customer_support_agent(session)
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def mock_upstream() -> Generator[AsyncMock, None, None]:
    response = httpx.Response(
        200,
        json={"id": 123, "status": "cancelled"},
        request=httpx.Request("POST", "http://demo-api:8000/api/orders/123/cancel"),
    )
    with patch("app.services.gateway_service.forward_to_demoshop", new_callable=AsyncMock) as mock:
        mock.return_value = response
        yield mock
