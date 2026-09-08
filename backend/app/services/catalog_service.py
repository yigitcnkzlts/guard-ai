from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.agent import Agent
from app.models.policy import Policy


def list_agents(db: Session, organization_id: UUID | None = None) -> list[Agent]:
    query=db.query(Agent)
    if organization_id is not None: query=query.filter(Agent.organization_id == organization_id)
    return query.order_by(Agent.name.asc()).all()


def get_agent(db: Session, agent_id: UUID, organization_id: UUID | None = None) -> Agent:
    agent = db.query(Agent).filter(Agent.id == agent_id, *([Agent.organization_id == organization_id] if organization_id else [])).first()
    if agent is None:
        raise NotFoundError(f"Agent {agent_id} not found")
    return agent


def list_policies(db: Session, organization_id: UUID | None = None) -> list[Policy]:
    query=db.query(Policy).join(Agent, Policy.agent_id == Agent.id)
    if organization_id is not None: query=query.filter(Agent.organization_id == organization_id)
    return query.order_by(Policy.name.asc()).all()


def get_policy(db: Session, policy_id: UUID, organization_id: UUID | None = None) -> Policy:
    query=db.query(Policy).join(Agent, Policy.agent_id == Agent.id).filter(Policy.id == policy_id)
    if organization_id is not None: query=query.filter(Agent.organization_id == organization_id)
    policy=query.first()
    if policy is None:
        raise NotFoundError(f"Policy {policy_id} not found")
    return policy
