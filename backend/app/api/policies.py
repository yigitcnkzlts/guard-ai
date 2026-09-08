from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.policy import PolicyRead
from app.services import catalog_service
from app.core.auth import RequestContext, get_request_context

router = APIRouter(prefix="/policies", tags=["policies"])


@router.get("", response_model=list[PolicyRead])
def list_policies(db: Session = Depends(get_db), context: RequestContext = Depends(get_request_context)) -> list[PolicyRead]:
    return catalog_service.list_policies(db, context.organization_id)


@router.get("/{policy_id}", response_model=PolicyRead)
def get_policy(policy_id: UUID, db: Session = Depends(get_db), context: RequestContext = Depends(get_request_context)) -> PolicyRead:
    return catalog_service.get_policy(db, policy_id, context.organization_id)
