from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.policy import Decision, RiskLevel
from app.schemas.security_event import SecurityEventRead
from app.services import event_service
from app.core.auth import RequestContext, get_request_context

router = APIRouter(prefix="/security-events", tags=["security-events"])


@router.get("", response_model=list[SecurityEventRead])
def list_security_events(
    db: Session = Depends(get_db),
    decision: Decision | None = Query(default=None),
    risk_level: RiskLevel | None = Query(default=None),
    agent_id: UUID | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    search: str | None = Query(default=None, max_length=200),
    context: RequestContext = Depends(get_request_context),
) -> list[SecurityEventRead]:
    return event_service.list_events(
        db,
        decision=decision,
        risk_level=risk_level,
        agent_id=agent_id,
        limit=limit,
        offset=offset,
        search=search,
        organization_id=context.organization_id,
    )
