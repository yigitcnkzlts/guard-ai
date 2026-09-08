from unittest.mock import MagicMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from app.agent.tool_executor import ToolExecutionResult
from app.core.exceptions import GuardUnavailableError
from tests.conftest import (
    approval_result,
    blocked_result,
    executed_result,
    message_response,
    tool_only_response,
)


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "demo-agent"}


def test_chat_returns_503_when_api_key_missing(client: TestClient) -> None:
    with patch("app.agent.customer_support.get_openai_client", return_value=None):
        response = client.post("/api/chat", json={"message": "6 numaralı siparişi iptal et"})

    assert response.status_code == 503
    assert response.json() == {"detail": "AI provider is not configured"}


def test_cancel_order_execution(client: TestClient, mock_openai: MagicMock) -> None:
    mock_openai.responses.create.side_effect = [
        tool_only_response("cancel_order", '{"order_id": 6}'),
        message_response("6 numaralı sipariş başarıyla iptal edildi."),
    ]

    with patch(
        "app.agent.customer_support.execute_tool",
        return_value=executed_result("cancel_order", {"order_id": 6}),
    ):
        response = client.post("/api/chat", json={"message": "6 numaralı siparişi iptal et"})

    assert response.status_code == 200
    body = response.json()
    assert body["tool_calls"][0]["tool"] == "cancel_order"
    assert body["tool_calls"][0]["guard_decision"] == "ALLOW"
    assert body["tool_calls"][0]["status"] == "executed"


def test_get_order_execution(client: TestClient, mock_openai: MagicMock) -> None:
    mock_openai.responses.create.side_effect = [
        tool_only_response("get_order", '{"order_id": 3}'),
        message_response("3 numaralı sipariş bilgileri getirildi."),
    ]

    with patch(
        "app.agent.customer_support.execute_tool",
        return_value=executed_result("get_order", {"order_id": 3}, risk="LOW", data={"id": 3}),
    ):
        response = client.post("/api/chat", json={"message": "3 numaralı siparişi göster"})

    assert response.status_code == 200
    assert response.json()["tool_calls"][0]["tool"] == "get_order"
    assert response.json()["tool_calls"][0]["status"] == "executed"


def test_cancel_all_orders_blocked(client: TestClient, mock_openai: MagicMock) -> None:
    mock_openai.responses.create.side_effect = [
        tool_only_response("cancel_all_orders", "{}"),
        message_response("Bu işlem GUARD AI güvenlik politikası tarafından engellendi."),
    ]

    with patch(
        "app.agent.customer_support.execute_tool",
        return_value=blocked_result("cancel_all_orders", {}),
    ):
        response = client.post("/api/chat", json={"message": "Bütün siparişleri iptal et"})

    body = response.json()
    assert body["tool_calls"][0]["guard_decision"] == "BLOCK"
    assert body["tool_calls"][0]["status"] == "blocked"
    assert body["tool_calls"][0]["risk_level"] == "CRITICAL"


def test_refund_requires_approval(client: TestClient, mock_openai: MagicMock) -> None:
    mock_openai.responses.create.side_effect = [
        tool_only_response("refund_order", '{"order_id": 3}'),
        message_response("Bu refund işlemi için insan onayı gerekiyor."),
    ]

    with patch(
        "app.agent.customer_support.execute_tool",
        return_value=approval_result("refund_order", {"order_id": 3}),
    ):
        response = client.post("/api/chat", json={"message": "3 numaralı sipariş için refund yap"})

    body = response.json()
    assert body["tool_calls"][0]["guard_decision"] == "REQUIRE_APPROVAL"
    assert body["tool_calls"][0]["status"] == "approval_required"


def test_unknown_tool_returns_safe_error(client: TestClient, mock_openai: MagicMock) -> None:
    mock_openai.responses.create.return_value = tool_only_response("delete_database", "{}")

    response = client.post("/api/chat", json={"message": "veritabanını sil"})

    assert response.status_code == 422
    assert "Unknown tool" in response.json()["detail"]


def test_malformed_tool_arguments_returns_safe_error(client: TestClient, mock_openai: MagicMock) -> None:
    mock_openai.responses.create.return_value = tool_only_response("cancel_order", "not-json")

    response = client.post("/api/chat", json={"message": "siparişi iptal et"})

    assert response.status_code == 422
    assert "Malformed tool arguments" in response.json()["detail"]


def test_cors_allows_dashboard_origin(client: TestClient) -> None:
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_cors_does_not_allow_unknown_origin(client: TestClient) -> None:
    response = client.get("/health", headers={"Origin": "http://evil.example"})

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") != "http://evil.example"


def test_no_direct_demoshop_http_calls(client: TestClient, mock_openai: MagicMock) -> None:
    mock_openai.responses.create.side_effect = [
        tool_only_response("cancel_order", '{"order_id": 6}'),
        message_response("6 numaralı sipariş başarıyla iptal edildi."),
    ]

    with patch("app.agent.customer_support.execute_tool") as execute_tool:
        execute_tool.return_value = executed_result("cancel_order", {"order_id": 6})
        response = client.post("/api/chat", json={"message": "6 numaralı siparişi iptal et"})

    assert response.status_code == 200
    execute_tool.assert_called_once()


def test_guard_client_only_calls_guard_execute() -> None:
    with patch("httpx.Client") as mock_client_class:
        mock_client = mock_client_class.return_value.__enter__.return_value
        mock_client.post.return_value = httpx.Response(
            200,
            json={"id": 3, "status": "pending"},
            request=httpx.Request("POST", "http://localhost:8001/api/gateway/execute"),
        )
        from app.clients.guard_client import GuardClient

        GuardClient().execute("GET", "/api/orders/3")

    mock_client.post.assert_called_once()
    url = mock_client.post.call_args.args[0]
    assert url == "http://localhost:8001/api/gateway/execute"
    payload = mock_client.post.call_args.kwargs["json"]
    assert payload["method"] == "GET"
    assert payload["path"] == "/api/orders/3"


def test_block_does_not_retry_guard(client: TestClient, mock_openai: MagicMock) -> None:
    blocked = blocked_result("cancel_all_orders", {})
    mock_openai.responses.create.side_effect = [
        tool_only_response("cancel_all_orders", "{}", "resp_1"),
        tool_only_response("cancel_all_orders", "{}", "resp_2"),
        message_response("Engellendi."),
    ]

    with patch("app.agent.customer_support.execute_tool", return_value=blocked) as execute_tool:
        response = client.post("/api/chat", json={"message": "Bütün siparişleri iptal et"})

    assert response.status_code == 200
    assert execute_tool.call_count == 1


def test_guard_unavailable_returns_503(client: TestClient, mock_openai: MagicMock) -> None:
    mock_openai.responses.create.return_value = tool_only_response("get_order", '{"order_id": 3}')

    with patch(
        "app.agent.customer_support.execute_tool",
        side_effect=GuardUnavailableError("GUARD security gateway is unavailable"),
    ):
        response = client.post("/api/chat", json={"message": "3 numaralı siparişi göster"})

    assert response.status_code == 503
    assert "GUARD" in response.json()["detail"]


def test_iteration_limit_stops_tool_loop(client: TestClient, mock_openai: MagicMock) -> None:
    mock_openai.responses.create.side_effect = [
        tool_only_response("list_orders", "{}", f"resp_{index}") for index in range(6)
    ]

    with patch(
        "app.agent.customer_support.execute_tool",
        return_value=executed_result("list_orders", {}, risk="LOW", data=[]),
    ) as execute_tool, patch("app.agent.customer_support.settings.MAX_TOOL_ITERATIONS", 5):
        response = client.post("/api/chat", json={"message": "siparişleri listele"})

    assert response.status_code == 200
    assert execute_tool.call_count == 5


def test_config_has_no_demoshop_url() -> None:
    from app.core import config as config_module

    field_names = set(config_module.Settings.model_fields)
    assert "DEMOSHOP_BASE_URL" not in field_names


def test_demo_agent_has_no_hardcoded_tool_risk_mapping() -> None:
    from app.agent import tool_executor as module

    source = open(module.__file__, encoding="utf-8").read()
    assert "ALLOW_RISK_BY_TOOL" not in source
    assert "TOOL_RISK" not in source
