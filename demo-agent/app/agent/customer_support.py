import json
from typing import Any

from app.agent.prompts import SYSTEM_PROMPT
from app.agent.tool_executor import ToolExecutionResult, execute_tool
from app.agent.tools import AGENT_SLUG, OPENAI_TOOLS, TOOL_NAMES
from app.clients.openai_client import get_openai_client
from app.core.config import settings
from app.core.exceptions import AgentProcessingError, ServiceUnavailableError
from app.schemas.chat import ChatResponse, ToolCall


def _parse_arguments(raw: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AgentProcessingError("Malformed tool arguments returned by AI provider") from exc
    if not isinstance(parsed, dict):
        raise AgentProcessingError("Malformed tool arguments returned by AI provider")
    return parsed


def _validate_tool_name(name: str) -> None:
    if name not in TOOL_NAMES:
        raise AgentProcessingError(f"Unknown tool selected: {name}")


def _tool_key(name: str, arguments: dict[str, Any]) -> str:
    return f"{name}:{json.dumps(arguments, sort_keys=True)}"


def _extract_function_calls(response: Any) -> list[dict[str, str]]:
    calls: list[dict[str, str]] = []
    for item in getattr(response, "output", []) or []:
        if getattr(item, "type", None) != "function_call":
            continue
        name = getattr(item, "name", None)
        call_id = getattr(item, "call_id", None)
        raw_arguments = getattr(item, "arguments", "{}")
        if not isinstance(name, str) or not isinstance(call_id, str):
            raise AgentProcessingError("Malformed function call returned by AI provider")
        _validate_tool_name(name)
        calls.append({"call_id": call_id, "name": name, "arguments": raw_arguments})
    return calls


def _extract_text(response: Any) -> str:
    for item in getattr(response, "output", []) or []:
        if getattr(item, "type", None) != "message":
            continue
        for content in getattr(item, "content", []) or []:
            if getattr(content, "type", None) == "output_text":
                text = getattr(content, "text", "")
                if isinstance(text, str) and text.strip():
                    return text.strip()
    return "İşlem tamamlandı."


def _to_tool_call(result: ToolExecutionResult) -> ToolCall:
    return ToolCall(
        tool=result.tool,
        arguments=result.arguments,
        guard_decision=result.guard_decision,
        risk_level=result.risk_level,
        status=result.status,
        reason=result.reason,
    )


def analyze_message(user_message: str) -> ChatResponse:
    client = get_openai_client()
    if client is None:
        raise ServiceUnavailableError()

    response = client.responses.create(
        model=settings.OPENAI_MODEL,
        instructions=SYSTEM_PROMPT,
        input=user_message,
        tools=OPENAI_TOOLS,
        tool_choice="auto",
        max_output_tokens=512,
        store=False,
    )

    executed_results: list[ToolExecutionResult] = []
    blocked_keys: set[str] = set()

    for _ in range(settings.MAX_TOOL_ITERATIONS):
        function_calls = _extract_function_calls(response)
        if not function_calls:
            break

        outputs: list[dict[str, str]] = []
        for function_call in function_calls:
            arguments = _parse_arguments(function_call["arguments"])
            key = _tool_key(function_call["name"], arguments)

            if key in blocked_keys:
                cached = next(
                    (
                        item
                        for item in executed_results
                        if _tool_key(item.tool, item.arguments) == key and item.status == "blocked"
                    ),
                    None,
                )
                if cached is not None:
                    outputs.append(
                        {
                            "type": "function_call_output",
                            "call_id": function_call["call_id"],
                            "output": json.dumps(cached.to_openai_output()),
                        }
                    )
                continue

            result = execute_tool(function_call["name"], arguments)
            executed_results.append(result)

            if result.status == "blocked":
                blocked_keys.add(key)

            outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": function_call["call_id"],
                    "output": json.dumps(result.to_openai_output()),
                }
            )

        if not outputs:
            break

        response = client.responses.create(
            model=settings.OPENAI_MODEL,
            previous_response_id=response.id,
            input=outputs,
            max_output_tokens=512,
            store=False,
        )

    return ChatResponse(
        message=_extract_text(response),
        agent=AGENT_SLUG,
        tool_calls=[_to_tool_call(result) for result in executed_results],
    )
