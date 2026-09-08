import hashlib
import json
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.governance import AuditLog


def append_audit_log(db: Session, *, actor: str, action: str, resource_type: str, resource_id: str | None = None, organization_id: UUID | None = None, details: dict | None = None) -> AuditLog:
    previous = db.query(AuditLog).order_by(AuditLog.created_at.desc(), AuditLog.id.desc()).first()
    previous_hash = previous.entry_hash if previous else None
    canonical = json.dumps({"actor": actor, "action": action, "resource_type": resource_type, "resource_id": resource_id, "organization_id": str(organization_id) if organization_id else None, "details": details or {}, "previous_hash": previous_hash}, sort_keys=True, separators=(",", ":"))
    entry = AuditLog(organization_id=organization_id, actor=actor, action=action, resource_type=resource_type, resource_id=resource_id, details=details, previous_hash=previous_hash, entry_hash=hashlib.sha256(canonical.encode()).hexdigest())
    db.add(entry); db.commit(); db.refresh(entry)
    return entry


def verify_chain(db: Session) -> bool:
    rows = db.query(AuditLog).order_by(AuditLog.created_at.asc(), AuditLog.id.asc()).all()
    previous_hash = None
    for row in rows:
        canonical = json.dumps({"actor": row.actor, "action": row.action, "resource_type": row.resource_type, "resource_id": row.resource_id, "organization_id": str(row.organization_id) if row.organization_id else None, "details": row.details or {}, "previous_hash": previous_hash}, sort_keys=True, separators=(",", ":"))
        if row.previous_hash != previous_hash or row.entry_hash != hashlib.sha256(canonical.encode()).hexdigest(): return False
        previous_hash = row.entry_hash
    return True
