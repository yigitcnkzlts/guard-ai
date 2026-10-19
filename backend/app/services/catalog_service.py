from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.agent import Agent
from app.models.policy import Policy
from app.repositories import catalog as repository


def list_agents(db: Session, organization_id: UUID | None = None) -> list[Agent]:
    return repository.list_agents(db, organization_id)


def get_agent(db: Session, agent_id: UUID, organization_id: UUID | None = None) -> Agent:
    agent = repository.get_agent(db, agent_id, organization_id)
    if agent is None:
        raise NotFoundError(f"Agent {agent_id} not found")
    return agent


def set_agent_active(agent: Agent, active: bool) -> Agent:
    agent.active = active
    return agent


def set_all_agents_active(db: Session, organization_id: UUID | None, active: bool) -> list[Agent]:
    agents = repository.list_agents(db, organization_id)
    for agent in agents:
        agent.active = active
    return agents


def list_policies(db: Session, organization_id: UUID | None = None) -> list[Policy]:
    return repository.list_policies(db, organization_id)


def get_policy(db: Session, policy_id: UUID, organization_id: UUID | None = None) -> Policy:
    policy=repository.get_policy(db, policy_id, organization_id)
    if policy is None:
        raise NotFoundError(f"Policy {policy_id} not found")
    return policy


def create_policy(db: Session, **values: object) -> Policy:
    policy = Policy(**values)
    db.add(policy)
    db.flush()
    return policy


def update_policy(policy: Policy, **values: object) -> Policy:
    for field, value in values.items():
        setattr(policy, field, value)
    policy.version += 1
    return policy
