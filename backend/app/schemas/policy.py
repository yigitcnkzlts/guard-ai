from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.policy import Decision, RiskLevel


class PolicyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    agent_id: UUID
    method: str
    path_pattern: str
    decision: Decision
    risk_level: RiskLevel
    description: str
    active: bool
    created_at: datetime
    updated_at: datetime
