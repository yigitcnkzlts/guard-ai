from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.agent import AgentEnvironment


class AgentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    description: str | None
    environment: AgentEnvironment
    active: bool
    created_at: datetime
    updated_at: datetime


class AgentStatusUpdate(BaseModel):
    active: bool
