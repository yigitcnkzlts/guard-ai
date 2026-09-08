from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.governance import ApprovalRequest, ApprovalStatus
from app.models.security_event import SecurityEvent

def create_for_event(db: Session, event: SecurityEvent, *, required_approvals: int = 1, ttl_minutes: int = 30) -> ApprovalRequest:
    approval = ApprovalRequest(organization_id=event.organization_id, security_event_id=event.id, status=ApprovalStatus.PENDING, required_approvals=max(1, required_approvals), approvals_received=0, expires_at=datetime.now(timezone.utc)+timedelta(minutes=ttl_minutes))
    db.add(approval); db.commit(); db.refresh(approval); return approval

def decide(db: Session, approval: ApprovalRequest, *, actor: str, approve: bool, reason: str | None = None) -> ApprovalRequest:
    if approval.status != ApprovalStatus.PENDING: raise ValueError("approval is no longer pending")
    if approve:
        approval.approvals_received += 1
        if approval.approvals_received >= approval.required_approvals: approval.status = ApprovalStatus.APPROVED
    else: approval.status = ApprovalStatus.REJECTED
    approval.decided_by=actor; approval.decision_reason=reason; db.commit(); db.refresh(approval); return approval
