import hmac
from dataclasses import dataclass
from enum import Enum
from uuid import UUID
from fastapi import Depends, Header, HTTPException
from app.core.config import settings

class Role(str, Enum):
    OWNER="owner"; SECURITY_ADMIN="security_admin"; POLICY_AUTHOR="policy_author"; REVIEWER="reviewer"; AUDITOR="auditor"

@dataclass(frozen=True)
class RequestContext:
    organization_id: UUID | None
    actor: str
    role: Role

def get_request_context(x_guard_admin_key: str | None=Header(default=None), x_organization_id: str | None=Header(default=None), x_actor: str | None=Header(default=None), x_role: str | None=Header(default=None)) -> RequestContext:
    if settings.ADMIN_API_KEY and not (x_guard_admin_key and hmac.compare_digest(x_guard_admin_key, settings.ADMIN_API_KEY)):
        raise HTTPException(status_code=401, detail="Invalid administrative API key")
    if settings.TENANT_ENFORCEMENT and not x_organization_id:
        raise HTTPException(status_code=400, detail="X-Organization-ID is required")
    try: organization_id=UUID(x_organization_id) if x_organization_id else None
    except ValueError as exc: raise HTTPException(status_code=400, detail="Invalid organization ID") from exc
    try: role=Role(x_role or Role.OWNER.value)
    except ValueError as exc: raise HTTPException(status_code=403, detail="Unknown role") from exc
    return RequestContext(organization_id=organization_id, actor=(x_actor or "system")[:255], role=role)

def require_roles(*allowed: Role):
    def dependency(context: RequestContext = Depends(get_request_context)) -> RequestContext:
        if context.role not in allowed: raise HTTPException(status_code=403, detail="Role is not allowed to perform this action")
        return context
    return dependency
