from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.policy import Decision, RiskLevel


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class GatewayExecuteRequest(BaseModel):
    agent: str = Field(..., min_length=1, max_length=255)
    method: HttpMethod
    path: str = Field(..., min_length=1, max_length=1024)
    body: Any | None = None

    @field_validator("method", mode="before")
    @classmethod
    def uppercase_method(cls, value: object) -> object:
        if isinstance(value, str):
            return value.upper()
        return value

    @field_validator("agent")
    @classmethod
    def strip_agent(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("agent must not be blank")
        return value


class GatewayExecuteResponse(BaseModel):
    decision: Decision
    risk_level: RiskLevel
    reason: str
    matched_policy_id: UUID | None = None
    upstream_status: int | None = None
    data: Any | None = None
