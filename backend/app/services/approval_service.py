from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.core.exceptions import ConflictError
from app.models.governance import ApprovalRequest, ApprovalStatus
from app.models.security_event import SecurityEvent

def create_for_event(db: Session, event: SecurityEvent, *, required_approvals: int = 1, ttl_minutes: int = 30) -> ApprovalRequest:
    approval = ApprovalRequest(organization_id=event.organization_id, security_event_id=event.id, status=ApprovalStatus.PENDING, required_approvals=max(1, required_approvals), approvals_received=0, expires_at=datetime.now(timezone.utc)+timedelta(minutes=ttl_minutes))
    db.add(approval); db.commit(); db.refresh(approval); return approval

def decide(db: Session, approval: ApprovalRequest, *, actor: str, approve: bool, reason: str | None = None, commit: bool = True) -> ApprovalRequest:
    now = datetime.now(timezone.utc)
    expires_at = approval.expires_at
    if expires_at is not None and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if approval.status == ApprovalStatus.PENDING and expires_at is not None and expires_at <= now:
        approval.status = ApprovalStatus.EXPIRED
        db.commit()
        db.refresh(approval)
        raise ConflictError("Approval request has expired")
    if approval.status != ApprovalStatus.PENDING:
        raise ConflictError(f"Approval request is already {approval.status.value.lower()}")
    if approve:
        approval.approvals_received += 1
        if approval.approvals_received >= approval.required_approvals: approval.status = ApprovalStatus.APPROVED
    else: approval.status = ApprovalStatus.REJECTED
    approval.decided_by = actor
    approval.decision_reason = reason
    if commit:
        db.commit()
        db.refresh(approval)
    else:
        db.flush()
    return approval
