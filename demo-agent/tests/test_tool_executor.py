from unittest.mock import MagicMock

import pytest

from app.agent import tool_executor
from app.agent.tool_executor import execute_tool, map_tool_to_guard_request
from app.clients.guard_client import GuardResponse
from app.core.exceptions import AgentProcessingError, GuardUnavailableError

POLICY_ID = "767d86bd-f621-4334-9528-15db0adf6f82"


def allow_body(
    risk_level: str = "MEDIUM",
    data: dict | None = None,
    upstream_status: int = 200,
) -> dict:
    return {
        "decision": "ALLOW",
        "risk_level": risk_level,
        "reason": "Request allowed by matched security policy",
        "matched_policy_id": POLICY_ID,
        "upstream_status": upstream_status,
        "data": data or {"id": 6, "status": "cancelled"},
    }


def test_get_order_maps_to_guard_get() -> None:
    method, path = map_tool_to_guard_request("get_order", {"order_id": 3})
    assert method == "GET"
    assert path == "/api/orders/3"


def test_cancel_order_maps_to_guard_post() -> None:
    method, path = map_tool_to_guard_request("cancel_order", {"order_id": 6})
    assert method == "POST"
    assert path == "/api/orders/6/cancel"


def test_refund_order_maps_to_guard_post() -> None:
    method, path = map_tool_to_guard_request("refund_order", {"order_id": 3})
    assert method == "POST"
    assert path == "/api/orders/3/refund"


def test_cancel_all_orders_maps_to_guard_post() -> None:
    method, path = map_tool_to_guard_request("cancel_all_orders", {})
    assert method == "POST"
    assert path == "/api/orders/cancel-all"


def test_allow_is_executed_from_guard_metadata() -> None:
    guard = MagicMock()
    guard.execute.return_value = GuardResponse(
        status_code=200,
        body=allow_body(risk_level="MEDIUM"),
        raw_text="{}",
    )

    result = execute_tool("cancel_order", {"order_id": 6}, guard_client=guard)

    assert result.status == "executed"
    assert result.guard_decision == "ALLOW"
    assert result.risk_level == "MEDIUM"
    assert result.matched_policy_id == POLICY_ID
    assert result.reason == "Request allowed by matched security policy"
    assert result.data == {"id": 6, "status": "cancelled"}
    guard.execute.assert_called_once_with(method="POST", path="/api/orders/6/cancel")


def test_allow_upstream_failure_uses_guard_risk_level() -> None:
    guard = MagicMock()
    guard.execute.return_value = GuardResponse(
        status_code=200,
        body=allow_body(risk_level="LOW", data={"detail": "Order not found"}, upstream_status=404),
        raw_text="{}",
    )

    result = execute_tool("get_order", {"order_id": 999}, guard_client=guard)

    assert result.status == "upstream_failed"
    assert result.guard_decision == "ALLOW"
    assert result.risk_level == "LOW"
    assert result.upstream_status == 404


def test_block_is_blocked() -> None:
    guard = MagicMock()
    guard.execute.return_value = GuardResponse(
        status_code=403,
        body={
            "decision": "BLOCK",
            "risk_level": "CRITICAL",
            "reason": "Bulk order cancellation is prohibited by security policy",
            "matched_policy_id": POLICY_ID,
            "data": None,
        },
        raw_text="{}",
    )

    result = execute_tool("cancel_all_orders", {}, guard_client=guard)

    assert result.status == "blocked"
    assert result.guard_decision == "BLOCK"
    assert result.risk_level == "CRITICAL"


def test_require_approval_is_not_executed() -> None:
    guard = MagicMock()
    guard.execute.return_value = GuardResponse(
        status_code=202,
        body={
            "decision": "REQUIRE_APPROVAL",
            "risk_level": "HIGH",
            "reason": "Refund operations require human approval",
            "matched_policy_id": POLICY_ID,
            "data": None,
        },
        raw_text="{}",
    )

    result = execute_tool("refund_order", {"order_id": 3}, guard_client=guard)

    assert result.status == "approval_required"
    assert result.guard_decision == "REQUIRE_APPROVAL"
    assert result.risk_level == "HIGH"


def test_guard_unavailable_is_fail_closed() -> None:
    guard = MagicMock()
    guard.execute.side_effect = GuardUnavailableError("GUARD security gateway is unavailable")

    with pytest.raises(GuardUnavailableError):
        execute_tool("get_order", {"order_id": 3}, guard_client=guard)


def test_guard_timeout_is_fail_closed() -> None:
    guard = MagicMock()
    guard.execute.side_effect = GuardUnavailableError("GUARD security gateway request timed out")

    with pytest.raises(GuardUnavailableError):
        execute_tool("cancel_order", {"order_id": 6}, guard_client=guard)


def test_invalid_order_id_is_rejected() -> None:
    with pytest.raises(AgentProcessingError):
        map_tool_to_guard_request("cancel_order", {"order_id": 0})


def test_unknown_tool_is_rejected() -> None:
    with pytest.raises(AgentProcessingError):
        map_tool_to_guard_request("delete_database", {})


def test_no_hardcoded_tool_risk_mapping() -> None:
    source = open(tool_executor.__file__, encoding="utf-8").read()
    assert "ALLOW_RISK_BY_TOOL" not in source
    assert "TOOL_RISK" not in source
