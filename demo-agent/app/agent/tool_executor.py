from dataclasses import dataclass
from typing import Any

from app.agent.tools import TOOL_NAMES
from app.clients.guard_client import GuardClient, GuardResponse
from app.core.exceptions import AgentProcessingError, GuardUnavailableError


@dataclass
class ToolExecutionResult:
    tool: str
    arguments: dict[str, Any]
    guard_decision: str | None
    risk_level: str | None
    status: str
    reason: str | None = None
    data: Any | None = None
    matched_policy_id: str | None = None
    upstream_status: int | None = None

    def to_openai_output(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "tool": self.tool,
            "arguments": self.arguments,
            "status": self.status,
        }
        if self.guard_decision is not None:
            payload["guard_decision"] = self.guard_decision
        if self.risk_level is not None:
            payload["risk_level"] = self.risk_level
        if self.reason is not None:
            payload["reason"] = self.reason
        if self.matched_policy_id is not None:
            payload["matched_policy_id"] = self.matched_policy_id
        if self.upstream_status is not None:
            payload["upstream_status"] = self.upstream_status
        if self.data is not None:
            payload["data"] = self.data
        return payload


def _validate_arguments(tool: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if tool not in TOOL_NAMES:
        raise AgentProcessingError(f"Unknown tool: {tool}")

    if tool in {"get_order", "cancel_order", "refund_order"}:
        order_id = arguments.get("order_id")
        if not isinstance(order_id, int) or order_id <= 0:
            raise AgentProcessingError("order_id must be a positive integer")

    if tool in {"list_orders", "cancel_all_orders"} and arguments:
        raise AgentProcessingError("Tool does not accept arguments")

    return arguments


def map_tool_to_guard_request(tool: str, arguments: dict[str, Any]) -> tuple[str, str]:
    validated = _validate_arguments(tool, arguments)

    if tool == "list_orders":
        return "GET", "/api/orders"
    if tool == "get_order":
        return "GET", f"/api/orders/{validated['order_id']}"
    if tool == "cancel_order":
        return "POST", f"/api/orders/{validated['order_id']}/cancel"
    if tool == "refund_order":
        return "POST", f"/api/orders/{validated['order_id']}/refund"
    if tool == "cancel_all_orders":
        return "POST", "/api/orders/cancel-all"

    raise AgentProcessingError(f"Unknown tool: {tool}")


def _normalize_guard_response(
    tool: str,
    arguments: dict[str, Any],
    response: GuardResponse,
) -> ToolExecutionResult:
    if response.status_code in {502, 503}:
        detail = response.body
        if isinstance(detail, dict):
            message = detail.get("detail", "GUARD security gateway is unavailable")
        else:
            message = "GUARD security gateway is unavailable"
        raise GuardUnavailableError(str(message))

    if not isinstance(response.body, dict) or "decision" not in response.body:
        raise AgentProcessingError("Unexpected GUARD response format")

    body = response.body
    decision = str(body.get("decision", ""))
    risk_level = body.get("risk_level")
    reason = body.get("reason")
    matched_policy_id = body.get("matched_policy_id")
    upstream_status = body.get("upstream_status")
    data = body.get("data")

    if decision == "BLOCK":
        return ToolExecutionResult(
            tool=tool,
            arguments=arguments,
            guard_decision=decision,
            risk_level=str(risk_level) if risk_level else None,
            status="blocked",
            reason=reason,
            matched_policy_id=matched_policy_id,
            data=data,
        )

    if decision == "REQUIRE_APPROVAL":
        return ToolExecutionResult(
            tool=tool,
            arguments=arguments,
            guard_decision=decision,
            risk_level=str(risk_level) if risk_level else None,
            status="approval_required",
            reason=reason,
            matched_policy_id=matched_policy_id,
            data=data,
        )

    if decision == "ALLOW":
        status = "executed"
        if isinstance(upstream_status, int) and upstream_status >= 400:
            status = "upstream_failed"
        return ToolExecutionResult(
            tool=tool,
            arguments=arguments,
            guard_decision=decision,
            risk_level=str(risk_level) if risk_level else None,
            status=status,
            reason=reason,
            matched_policy_id=matched_policy_id,
            upstream_status=upstream_status if isinstance(upstream_status, int) else None,
            data=data,
        )

    raise AgentProcessingError(f"Unexpected GUARD decision: {decision}")


def execute_tool(
    tool: str,
    arguments: dict[str, Any],
    guard_client: GuardClient | None = None,
) -> ToolExecutionResult:
    method, path = map_tool_to_guard_request(tool, arguments)
    client = guard_client or GuardClient()
    response = client.execute(method=method, path=path)
    return _normalize_guard_response(tool, arguments, response)
