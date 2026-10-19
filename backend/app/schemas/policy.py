from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

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


class PolicyWrite(BaseModel):
    name: str = Field(min_length=3, max_length=255)
    agent_id: UUID
    method: str = Field(min_length=3, max_length=16)
    path_pattern: str = Field(min_length=1, max_length=512)
    decision: Decision
    risk_level: RiskLevel
    description: str = Field(min_length=1, max_length=2000)
    active: bool = True
    priority: int = Field(default=100, ge=0, le=10000)

    @field_validator("name", "description")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value must not be blank")
        return value

    @field_validator("method")
    @classmethod
    def normalize_method(cls, value: str) -> str:
        return value.upper()

    @field_validator("path_pattern")
    @classmethod
    def validate_path_pattern(cls, value: str) -> str:
        value = value.strip()
        if not value.startswith("/"):
            raise ValueError("Path pattern must start with /")
        return value


class PolicyCreate(PolicyWrite):
    pass


class PolicyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=255)
    agent_id: UUID | None = None
    method: str | None = Field(default=None, min_length=3, max_length=16)
    path_pattern: str | None = Field(default=None, min_length=1, max_length=512)
    decision: Decision | None = None
    risk_level: RiskLevel | None = None
    description: str | None = Field(default=None, min_length=1, max_length=2000)
    active: bool | None = None
    priority: int | None = Field(default=None, ge=0, le=10000)

    @field_validator("name", "description")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("Value must not be blank")
        return value

    @field_validator("method")
    @classmethod
    def normalize_optional_method(cls, value: str | None) -> str | None:
        return value.upper() if value is not None else None

    @field_validator("path_pattern")
    @classmethod
    def validate_optional_path_pattern(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value.startswith("/"):
            raise ValueError("Path pattern must start with /")
        return value
