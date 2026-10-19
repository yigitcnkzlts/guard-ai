from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.auth import RequestContext, Role, get_request_context, require_roles
from app.core.exceptions import NotFoundError
from app.database.session import get_db
from app.models.governance import ApprovalRequest, ApprovalStatus
from app.schemas.approval import ApprovalDecision, ApprovalRead
from app.services import approval_service, audit_service

router=APIRouter(prefix="/approvals",tags=["approvals"])

@router.get("",response_model=list[ApprovalRead])
def list_approvals(status: ApprovalStatus | None=None, db:Session=Depends(get_db), context:RequestContext=Depends(get_request_context)):
    query=db.query(ApprovalRequest)
    if context.organization_id is not None: query=query.filter(ApprovalRequest.organization_id==context.organization_id)
    if status is not None: query=query.filter(ApprovalRequest.status==status)
    return query.order_by(ApprovalRequest.created_at.desc()).all()

@router.post("/{approval_id}/decision",response_model=ApprovalRead)
def decide_approval(approval_id:UUID,payload:ApprovalDecision,db:Session=Depends(get_db),context:RequestContext=Depends(require_roles(Role.OWNER,Role.SECURITY_ADMIN,Role.REVIEWER))):
    query=db.query(ApprovalRequest).filter(ApprovalRequest.id==approval_id).with_for_update()
    if context.organization_id is not None: query=query.filter(ApprovalRequest.organization_id==context.organization_id)
    approval=query.first()
    if approval is None: raise NotFoundError(f"Approval {approval_id} not found")
    result=approval_service.decide(db,approval,actor=context.actor,approve=payload.approve,reason=payload.reason)
    audit_service.append_audit_log(db,actor=context.actor,action="approval.approved" if payload.approve else "approval.rejected",resource_type="approval_request",resource_id=str(result.id),organization_id=context.organization_id,details={"reason":payload.reason})
    return result
