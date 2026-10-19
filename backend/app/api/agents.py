from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.agent import AgentRead, AgentStatusUpdate
from app.services import audit_service, catalog_service
from app.core.auth import RequestContext, Role, get_request_context, require_roles

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("", response_model=list[AgentRead])
def list_agents(db: Session = Depends(get_db), context: RequestContext = Depends(get_request_context)) -> list[AgentRead]:
    return catalog_service.list_agents(db, context.organization_id)


@router.get("/{agent_id}", response_model=AgentRead)
def get_agent(agent_id: UUID, db: Session = Depends(get_db), context: RequestContext = Depends(get_request_context)) -> AgentRead:
    return catalog_service.get_agent(db, agent_id, context.organization_id)


@router.patch("/{agent_id}/status", response_model=AgentRead)
def update_agent_status(agent_id: UUID, payload: AgentStatusUpdate, db: Session = Depends(get_db), context: RequestContext = Depends(require_roles(Role.OWNER, Role.SECURITY_ADMIN))) -> AgentRead:
    agent = catalog_service.get_agent(db, agent_id, context.organization_id)
    try:
        catalog_service.set_agent_active(agent, payload.active)
        audit_service.append_audit_log(db, actor=context.actor, action="agent.resumed" if payload.active else "agent.paused", resource_type="agent", resource_id=str(agent.id), organization_id=agent.organization_id, details={"active": payload.active}, commit=False)
        db.commit()
        db.refresh(agent)
        return agent
    except Exception:
        db.rollback()
        raise


@router.post("/actions/set-all-status", response_model=list[AgentRead])
def update_all_agent_status(payload: AgentStatusUpdate, db: Session = Depends(get_db), context: RequestContext = Depends(require_roles(Role.OWNER, Role.SECURITY_ADMIN))) -> list[AgentRead]:
    try:
        agents = catalog_service.set_all_agents_active(db, context.organization_id, payload.active)
        audit_service.append_audit_log(db, actor=context.actor, action="agents.resumed_all" if payload.active else "agents.lockdown", resource_type="organization", resource_id=str(context.organization_id) if context.organization_id else "default", organization_id=context.organization_id, details={"active": payload.active, "agent_count": len(agents)}, commit=False)
        db.commit()
        for agent in agents:
            db.refresh(agent)
        return agents
    except Exception:
        db.rollback()
        raise
