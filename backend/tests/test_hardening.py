from app.core.gateway_guard import IdempotencyStore, RateLimiter
from app.models.governance import ApprovalRequest
from app.services.anomaly_service import detect_volume_anomaly


def test_rate_limiter_enforces_window() -> None:
    limiter = RateLimiter(limit=2, window_seconds=10)
    assert limiter.allow("agent", now=0)
    assert limiter.allow("agent", now=1)
    assert not limiter.allow("agent", now=2)
    assert limiter.allow("agent", now=11)


def test_idempotency_store_expires_values() -> None:
    store = IdempotencyStore()
    store.put("request", {"ok": True}, ttl_seconds=5, now=10)
    assert store.get("request", now=12) == {"ok": True}
    assert store.get("request", now=16) is None


def test_volume_anomaly_has_explainable_result() -> None:
    result = detect_volume_anomaly(current_count=50, baseline_average=10)
    assert result.anomalous is True
    assert result.score > 1
    assert "baseline" in result.reason


def test_approval_request_is_persisted(client, db_session) -> None:
    response = client.post("/api/gateway/execute", json={"agent":"customer-support-agent","method":"POST","path":"/api/orders/123/refund","body":None})
    assert response.status_code == 202
    approval = db_session.query(ApprovalRequest).one()
    assert approval.status.value == "PENDING"
    assert approval.required_approvals == 1


def test_security_headers_and_request_id(client) -> None:
    response = client.get("/health")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["x-request-id"]
