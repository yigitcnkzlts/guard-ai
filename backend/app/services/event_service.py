from typing import Any
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.security import redact_secrets
from app.models.policy import Decision, RiskLevel
from app.models.security_event import SecurityEvent


def record_event(
    db: Session,
    *,
    agent_id: UUID,
    method: str,
    path: str,
    decision: Decision,
    risk_level: RiskLevel,
    reason: str,
    matched_policy_id: UUID | None = None,
    request_body: Any | None = None,
    organization_id: UUID | None = None,
    request_id: str | None = None,
    latency_ms: int | None = None,
) -> SecurityEvent:
    event = SecurityEvent(
        agent_id=agent_id,
        method=method,
        path=path,
        decision=decision,
        risk_level=risk_level,
        matched_policy_id=matched_policy_id,
        reason=reason,
        request_body=redact_secrets(request_body),
        organization_id=organization_id,
        request_id=request_id,
        latency_ms=latency_ms,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def list_events(
    db: Session,
    *,
    decision: Decision | None = None,
    risk_level: RiskLevel | None = None,
    agent_id: UUID | None = None,
    limit: int = 50,
    offset: int = 0,
    search: str | None = None,
    organization_id: UUID | None = None,
) -> list[SecurityEvent]:
    clamped_limit = min(max(limit, 1), 200)
    query = db.query(SecurityEvent).order_by(SecurityEvent.created_at.desc(), SecurityEvent.id.desc())
    if organization_id is not None:
        query = query.filter(SecurityEvent.organization_id == organization_id)
    if decision is not None:
        query = query.filter(SecurityEvent.decision == decision)
    if risk_level is not None:
        query = query.filter(SecurityEvent.risk_level == risk_level)
    if agent_id is not None:
        query = query.filter(SecurityEvent.agent_id == agent_id)
    if search and search.strip():
        # Treat SQL wildcard characters as literal search text.
        term = search.strip().replace("/", "//").replace("%", "/%").replace("_", "/_")
        query = query.filter(or_(
            SecurityEvent.path.ilike(f"%{term}%", escape="/"),
            SecurityEvent.reason.ilike(f"%{term}%", escape="/"),
        ))
    return query.offset(max(offset, 0)).limit(clamped_limit).all()
