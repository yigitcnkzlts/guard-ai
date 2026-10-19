from app.models.agent import Agent
from app.models.governance import AuditLog
from app.models.policy import Policy
from uuid import UUID


def test_policy_author_can_create_and_update_policy(client, db_session):
    agent = db_session.query(Agent).filter(Agent.slug == "customer-support-agent").one()
    created = client.post(
        "/api/policies",
        headers={"X-Role": "policy_author", "X-Actor": "author@example.com"},
        json={
            "name": "Review account deletion",
            "agent_id": str(agent.id),
            "method": "post",
            "path_pattern": "/api/accounts/{account_id}/delete",
            "decision": "REQUIRE_APPROVAL",
            "risk_level": "HIGH",
            "description": "Require a reviewer before deleting an account.",
        },
    )
    assert created.status_code == 201
    assert created.json()["method"] == "POST"

    policy_id = created.json()["id"]
    updated = client.patch(
        f"/api/policies/{policy_id}",
        headers={"X-Role": "policy_author", "X-Actor": "author@example.com"},
        json={"decision": "BLOCK", "description": "Block account deletion.", "active": False},
    )
    assert updated.status_code == 200
    assert updated.json()["decision"] == "BLOCK"
    assert updated.json()["active"] is False
    assert db_session.query(Policy).filter(Policy.id == UUID(policy_id)).one().version == 2
    assert [row.action for row in db_session.query(AuditLog).order_by(AuditLog.created_at).all()] == ["policy.created", "policy.updated"]


def test_auditor_cannot_create_policy(client, db_session):
    agent = db_session.query(Agent).filter(Agent.slug == "customer-support-agent").one()
    response = client.post(
        "/api/policies",
        headers={"X-Role": "auditor"},
        json={
            "name": "Blocked policy",
            "agent_id": str(agent.id),
            "method": "POST",
            "path_pattern": "/api/test",
            "decision": "BLOCK",
            "risk_level": "HIGH",
            "description": "Should not be created.",
        },
    )
    assert response.status_code == 403
    assert db_session.query(Policy).filter(Policy.name == "Blocked policy").count() == 0


def test_policy_write_validates_path(client, db_session):
    agent = db_session.query(Agent).filter(Agent.slug == "customer-support-agent").one()
    response = client.post(
        "/api/policies",
        json={
            "name": "Invalid path",
            "agent_id": str(agent.id),
            "method": "POST",
            "path_pattern": "api/test",
            "decision": "BLOCK",
            "risk_level": "HIGH",
            "description": "Invalid path should be rejected.",
        },
    )
    assert response.status_code == 422
