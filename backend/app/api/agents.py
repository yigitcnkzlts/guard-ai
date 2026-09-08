from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.agent import AgentRead
from app.services import catalog_service
from app.core.auth import RequestContext, get_request_context

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("", response_model=list[AgentRead])
def list_agents(db: Session = Depends(get_db), context: RequestContext = Depends(get_request_context)) -> list[AgentRead]:
    return catalog_service.list_agents(db, context.organization_id)


@router.get("/{agent_id}", response_model=AgentRead)
def get_agent(agent_id: UUID, db: Session = Depends(get_db), context: RequestContext = Depends(get_request_context)) -> AgentRead:
    return catalog_service.get_agent(db, agent_id, context.organization_id)
