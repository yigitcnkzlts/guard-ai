from app.models.agent import Agent
from app.models.governance import AuditLog


def test_security_admin_can_pause_and_resume_agent(client, db_session):
    agent = db_session.query(Agent).filter(Agent.slug == "customer-support-agent").one()
    paused = client.patch(f"/api/agents/{agent.id}/status", headers={"X-Role": "security_admin", "X-Actor": "admin@example.com"}, json={"active": False})
    assert paused.status_code == 200
    assert paused.json()["active"] is False
    blocked = client.post("/api/gateway/execute", json={"agent": agent.slug, "method": "GET", "path": "/api/orders/123", "body": None})
    assert blocked.status_code == 403
    assert blocked.json()["reason"] == "Agent is inactive"
    resumed = client.patch(f"/api/agents/{agent.id}/status", headers={"X-Role": "security_admin"}, json={"active": True})
    assert resumed.status_code == 200
    assert resumed.json()["active"] is True


def test_lockdown_and_resume_all_are_persisted_and_audited(client, db_session):
    locked = client.post("/api/agents/actions/set-all-status", headers={"X-Role": "owner"}, json={"active": False})
    assert locked.status_code == 200
    assert locked.json() and all(not agent["active"] for agent in locked.json())
    assert db_session.query(Agent).filter(Agent.active.is_(True)).count() == 0
    resumed = client.post("/api/agents/actions/set-all-status", headers={"X-Role": "owner"}, json={"active": True})
    assert resumed.status_code == 200
    assert all(agent["active"] for agent in resumed.json())
    actions = [row.action for row in db_session.query(AuditLog).order_by(AuditLog.created_at).all()]
    assert actions == ["agents.lockdown", "agents.resumed_all"]


def test_auditor_cannot_pause_agent(client, db_session):
    agent = db_session.query(Agent).filter(Agent.slug == "customer-support-agent").one()
    response = client.patch(f"/api/agents/{agent.id}/status", headers={"X-Role": "auditor"}, json={"active": False})
    assert response.status_code == 403
    db_session.refresh(agent)
    assert agent.active is True
