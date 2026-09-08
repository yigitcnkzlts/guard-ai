from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.policy import Decision, RiskLevel


class SecurityEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    agent_id: UUID
    method: str
    path: str
    decision: Decision
    risk_level: RiskLevel
    matched_policy_id: UUID | None
    reason: str
    request_body: Any | None
    created_at: datetime


class SecurityEventListQuery(BaseModel):
    decision: Decision | None = None
    risk_level: RiskLevel | None = None
    agent_id: UUID | None = None
    limit: int = Field(default=50, ge=1, le=200)
