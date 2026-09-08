from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)


class ToolCall(BaseModel):
    tool: str
    arguments: dict[str, Any]
    guard_decision: str | None = None
    risk_level: str | None = None
    status: str
    reason: str | None = None


class ChatResponse(BaseModel):
    message: str
    agent: str
    tool_calls: list[ToolCall] = Field(default_factory=list)
