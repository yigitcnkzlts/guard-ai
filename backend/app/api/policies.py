from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.policy import PolicyCreate, PolicyRead, PolicyUpdate
from app.services import audit_service, catalog_service
from app.core.auth import RequestContext, Role, get_request_context, require_roles

router = APIRouter(prefix="/policies", tags=["policies"])


@router.get("", response_model=list[PolicyRead])
def list_policies(db: Session = Depends(get_db), context: RequestContext = Depends(get_request_context)) -> list[PolicyRead]:
    return catalog_service.list_policies(db, context.organization_id)


@router.get("/{policy_id}", response_model=PolicyRead)
def get_policy(policy_id: UUID, db: Session = Depends(get_db), context: RequestContext = Depends(get_request_context)) -> PolicyRead:
    return catalog_service.get_policy(db, policy_id, context.organization_id)


@router.post("", response_model=PolicyRead, status_code=201)
def create_policy(payload: PolicyCreate, db: Session = Depends(get_db), context: RequestContext = Depends(require_roles(Role.OWNER, Role.SECURITY_ADMIN, Role.POLICY_AUTHOR))) -> PolicyRead:
    agent = catalog_service.get_agent(db, payload.agent_id, context.organization_id)
    try:
        policy = catalog_service.create_policy(db, **payload.model_dump())
        audit_service.append_audit_log(db, actor=context.actor, action="policy.created", resource_type="policy", resource_id=str(policy.id), organization_id=agent.organization_id, details={"name": policy.name, "version": policy.version}, commit=False)
        db.commit()
        db.refresh(policy)
        return policy
    except Exception:
        db.rollback()
        raise


@router.patch("/{policy_id}", response_model=PolicyRead)
def update_policy(policy_id: UUID, payload: PolicyUpdate, db: Session = Depends(get_db), context: RequestContext = Depends(require_roles(Role.OWNER, Role.SECURITY_ADMIN, Role.POLICY_AUTHOR))) -> PolicyRead:
    policy = catalog_service.get_policy(db, policy_id, context.organization_id)
    changes = payload.model_dump(exclude_unset=True)
    target_agent = catalog_service.get_agent(db, changes.get("agent_id", policy.agent_id), context.organization_id)
    try:
        catalog_service.update_policy(policy, **changes)
        audit_service.append_audit_log(db, actor=context.actor, action="policy.updated", resource_type="policy", resource_id=str(policy.id), organization_id=target_agent.organization_id, details={"fields": sorted(changes), "version": policy.version}, commit=False)
        db.commit()
        db.refresh(policy)
        return policy
    except Exception:
        db.rollback()
        raise
