from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.models.governance import ApprovalStatus

class ApprovalRead(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id: UUID; organization_id: UUID | None; security_event_id: UUID; status: ApprovalStatus
    required_approvals: int; approvals_received: int; decided_by: str | None; decision_reason: str | None; expires_at: datetime | None; created_at: datetime

class ApprovalDecision(BaseModel):
    approve: bool
    reason: str | None = Field(default=None, max_length=1000)
