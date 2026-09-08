from unittest.mock import AsyncMock

import httpx
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.agent import Agent, AgentEnvironment
from app.models.security_event import SecurityEvent


def _execute(client: TestClient, method: str, path: str, body: dict | None = None):
    return client.post(
        "/api/gateway/execute",
        json={
            "agent": "customer-support-agent",
            "method": method,
            "path": path,
            "body": body,
        },
    )


def test_get_order_policy_allows(client: TestClient, mock_upstream: AsyncMock) -> None:
    response = _execute(client, "GET", "/api/orders/123")

    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "ALLOW"
    assert body["risk_level"] == "LOW"
    assert body["matched_policy_id"] is not None
    assert body["upstream_status"] == 200
    mock_upstream.assert_awaited_once()
    method, path, body_arg = mock_upstream.await_args.args
    assert method == "GET"
    assert path == "/api/orders/123"
    assert body_arg is None


def test_cancel_single_order_policy_allows(client: TestClient, mock_upstream: AsyncMock) -> None:
    response = _execute(client, "POST", "/api/orders/123/cancel")

    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "ALLOW"
    assert body["risk_level"] == "MEDIUM"
    assert body["matched_policy_id"] is not None
    mock_upstream.assert_awaited_once()
    method, path, _body = mock_upstream.await_args.args
    assert method == "POST"
    assert path == "/api/orders/123/cancel"


def test_allow_forwards_request_to_demoshop(client: TestClient, mock_upstream: AsyncMock) -> None:
    response = _execute(client, "POST", "/api/orders/456/cancel")

    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "ALLOW"
    assert body["risk_level"] == "MEDIUM"
    assert body["upstream_status"] == 200
    assert body["data"]["id"] == 123
    mock_upstream.assert_awaited_once()
    method, path, body_arg = mock_upstream.await_args.args
    assert method == "POST"
    assert path == "/api/orders/456/cancel"
    assert body_arg is None


def test_allow_includes_upstream_data_and_metadata(client: TestClient, mock_upstream: AsyncMock) -> None:
    response = _execute(client, "POST", "/api/orders/456/cancel")

    body = response.json()
    assert body["reason"] == "Request allowed by matched security policy"
    assert body["data"] == {"id": 123, "status": "cancelled"}


def test_allow_upstream_failure_preserves_security_decision(client: TestClient, mock_upstream: AsyncMock) -> None:
    mock_upstream.return_value = httpx.Response(
        404,
        json={"detail": "Order not found"},
        request=httpx.Request("GET", "http://demo-api:8000/api/orders/999"),
    )

    response = _execute(client, "GET", "/api/orders/999")

    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "ALLOW"
    assert body["risk_level"] == "LOW"
    assert body["upstream_status"] == 404
    assert body["data"] == {"detail": "Order not found"}


def test_cancel_all_is_blocked(client: TestClient, mock_upstream: AsyncMock) -> None:
    response = _execute(client, "POST", "/api/orders/cancel-all")

    assert response.status_code == 403
    body = response.json()
    assert body["decision"] == "BLOCK"
    assert body["risk_level"] == "CRITICAL"
    assert body["reason"] == "Bulk order cancellation is prohibited by security policy"
    assert body["matched_policy_id"] is not None
    assert body["data"] is None
    mock_upstream.assert_not_awaited()


def test_block_does_not_call_demoshop(client: TestClient, mock_upstream: AsyncMock) -> None:
    _execute(client, "POST", "/api/orders/cancel-all")
    mock_upstream.assert_not_awaited()


def test_refund_requires_approval(client: TestClient, mock_upstream: AsyncMock) -> None:
    response = _execute(client, "POST", "/api/orders/123/refund")

    assert response.status_code == 202
    body = response.json()
    assert body["decision"] == "REQUIRE_APPROVAL"
    assert body["risk_level"] == "HIGH"
    assert body["reason"] == "Refund operations require human approval"
    assert body["matched_policy_id"] is not None
    assert body["data"] is None


def test_require_approval_does_not_call_demoshop(client: TestClient, mock_upstream: AsyncMock) -> None:
    _execute(client, "POST", "/api/orders/123/refund")
    mock_upstream.assert_not_awaited()


def test_unknown_endpoint_is_blocked(client: TestClient, mock_upstream: AsyncMock) -> None:
    response = _execute(client, "DELETE", "/api/orders/123")

    assert response.status_code == 403
    body = response.json()
    assert body["decision"] == "BLOCK"
    assert body["risk_level"] == "HIGH"
    assert body["reason"] == "No matching security policy found"
    assert body["matched_policy_id"] is None
    assert body["data"] is None
    mock_upstream.assert_not_awaited()


def test_dynamic_order_id_matching_through_gateway(client: TestClient, mock_upstream: AsyncMock) -> None:
    first = _execute(client, "POST", "/api/orders/123/cancel")
    second = _execute(client, "POST", "/api/orders/999/cancel")

    assert first.status_code == 200
    assert second.status_code == 200
    assert mock_upstream.await_count == 2
    assert mock_upstream.await_args_list[0].args[1] == "/api/orders/123/cancel"
    assert mock_upstream.await_args_list[1].args[1] == "/api/orders/999/cancel"


def test_security_event_is_recorded_for_each_decision(
    client: TestClient,
    mock_upstream: AsyncMock,
    db_session: Session,
) -> None:
    _execute(client, "GET", "/api/orders/123")
    _execute(client, "POST", "/api/orders/cancel-all")
    _execute(client, "POST", "/api/orders/123/refund")

    events_response = client.get("/api/security-events")
    assert events_response.status_code == 200
    events = events_response.json()
    assert len(events) == 3
    decisions = {event["decision"] for event in events}
    assert decisions == {"ALLOW", "BLOCK", "REQUIRE_APPROVAL"}

    stored = db_session.query(SecurityEvent).all()
    assert len(stored) == 3
    assert all(event.matched_policy_id is not None for event in stored)


def test_inactive_agent_is_blocked(
    client: TestClient,
    mock_upstream: AsyncMock,
    db_session: Session,
) -> None:
    inactive = Agent(
        name="Inactive Agent",
        slug="inactive-agent",
        description=None,
        environment=AgentEnvironment.DEVELOPMENT,
        active=False,
    )
    db_session.add(inactive)
    db_session.commit()

    response = client.post(
        "/api/gateway/execute",
        json={
            "agent": "inactive-agent",
            "method": "GET",
            "path": "/api/orders/123",
            "body": None,
        },
    )

    assert response.status_code == 403
    body = response.json()
    assert body["decision"] == "BLOCK"
    assert body["risk_level"] == "HIGH"
    assert body["reason"] == "Agent is inactive"
    assert body["matched_policy_id"] is None
    mock_upstream.assert_not_awaited()
