from uuid import UUID
from sqlalchemy.orm import Session
from app.models.agent import Agent
from app.models.policy import Policy

def agents_query(db:Session,organization_id:UUID|None=None):
    query=db.query(Agent)
    return query.filter(Agent.organization_id==organization_id) if organization_id else query

def policies_query(db:Session,organization_id:UUID|None=None):
    query=db.query(Policy).join(Agent,Policy.agent_id==Agent.id)
    return query.filter(Agent.organization_id==organization_id) if organization_id else query

def list_agents(db:Session,organization_id:UUID|None=None)->list[Agent]: return agents_query(db,organization_id).order_by(Agent.name.asc()).all()
def get_agent(db:Session,agent_id:UUID,organization_id:UUID|None=None)->Agent|None: return agents_query(db,organization_id).filter(Agent.id==agent_id).first()
def list_policies(db:Session,organization_id:UUID|None=None)->list[Policy]: return policies_query(db,organization_id).order_by(Policy.name.asc()).all()
def get_policy(db:Session,policy_id:UUID,organization_id:UUID|None=None)->Policy|None: return policies_query(db,organization_id).filter(Policy.id==policy_id).first()
