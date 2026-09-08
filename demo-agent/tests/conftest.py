import os

os.environ.setdefault("OPENAI_API_KEY", "")
os.environ.setdefault("OPENAI_MODEL", "gpt-4.1-mini")
os.environ.setdefault("MAX_TOOL_ITERATIONS", "5")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000")
os.environ.setdefault("GUARD_API_URL", "http://localhost:8001")
os.environ.setdefault("GUARD_TIMEOUT_SECONDS", "10")

from collections.abc import Generator
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from app.agent.tool_executor import ToolExecutionResult, execute_tool
from app.clients.guard_client import GuardClient, GuardResponse
from app.main import app


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


def function_call(name: str, arguments: str, call_id: str = "call_1") -> SimpleNamespace:
    return SimpleNamespace(type="function_call", name=name, arguments=arguments, call_id=call_id)


def message_response(text: str, response_id: str = "resp_final") -> SimpleNamespace:
    return SimpleNamespace(
        id=response_id,
        output=[
            SimpleNamespace(
                type="message",
                content=[SimpleNamespace(type="output_text", text=text)],
            )
        ],
    )


def tool_only_response(name: str, arguments: str, response_id: str = "resp_tool") -> SimpleNamespace:
    return SimpleNamespace(id=response_id, output=[function_call(name, arguments)])


@pytest.fixture()
def mock_openai() -> Generator[MagicMock, None, None]:
    mock_client = MagicMock()
    with patch("app.agent.customer_support.get_openai_client", return_value=mock_client):
        yield mock_client


def executed_result(tool: str, arguments: dict, risk: str = "MEDIUM", data: dict | None = None) -> ToolExecutionResult:
    return ToolExecutionResult(
        tool=tool,
        arguments=arguments,
        guard_decision="ALLOW",
        risk_level=risk,
        status="executed",
        reason="Request allowed by matched security policy",
        matched_policy_id="767d86bd-f621-4334-9528-15db0adf6f82",
        upstream_status=200,
        data=data or {"id": arguments.get("order_id", 1), "status": "cancelled"},
    )


def blocked_result(tool: str, arguments: dict) -> ToolExecutionResult:
    return ToolExecutionResult(
        tool=tool,
        arguments=arguments,
        guard_decision="BLOCK",
        risk_level="CRITICAL",
        status="blocked",
        reason="Bulk order cancellation is prohibited by security policy",
        matched_policy_id="8a6e892d-a8de-4195-bb74-d53d2ee92652",
        data=None,
    )


def approval_result(tool: str, arguments: dict) -> ToolExecutionResult:
    return ToolExecutionResult(
        tool=tool,
        arguments=arguments,
        guard_decision="REQUIRE_APPROVAL",
        risk_level="HIGH",
        status="approval_required",
        reason="Refund operations require human approval",
        matched_policy_id="32a54eb2-35fc-4236-97a5-e9bcd3aa89a1",
        data=None,
    )
