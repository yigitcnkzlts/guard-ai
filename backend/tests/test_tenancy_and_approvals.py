from app.models.agent import Agent, AgentEnvironment
from app.models.governance import ApprovalRequest, Organization


def test_agent_list_is_scoped_by_organization(client, db_session):
    first=Organization(name="First",slug="first"); second=Organization(name="Second",slug="second")
    db_session.add_all([first,second]); db_session.flush()
    db_session.add_all([Agent(name="First Agent",slug="first-agent",environment=AgentEnvironment.PRODUCTION,organization_id=first.id),Agent(name="Second Agent",slug="second-agent",environment=AgentEnvironment.PRODUCTION,organization_id=second.id)])
    db_session.commit()
    response=client.get("/api/agents",headers={"X-Organization-ID":str(first.id)})
    assert response.status_code==200
    assert [row["name"] for row in response.json()]==["First Agent"]


def test_approval_decision_enforces_role(client, db_session):
    created=client.post("/api/gateway/execute",json={"agent":"customer-support-agent","method":"POST","path":"/api/orders/123/refund","body":None})
    assert created.status_code==202
    approval=db_session.query(ApprovalRequest).one()
    forbidden=client.post(f"/api/approvals/{approval.id}/decision",headers={"X-Role":"auditor","X-Actor":"audit@example.com"},json={"approve":True})
    assert forbidden.status_code==403
    accepted=client.post(f"/api/approvals/{approval.id}/decision",headers={"X-Role":"reviewer","X-Actor":"reviewer@example.com"},json={"approve":True,"reason":"Verified customer request"})
    assert accepted.status_code==200
    assert accepted.json()["status"]=="APPROVED"


def test_idempotency_header_replays_gateway_response(client, mock_upstream):
    payload={"agent":"customer-support-agent","method":"GET","path":"/api/orders/123","body":None}
    first=client.post("/api/gateway/execute",headers={"Idempotency-Key":"order-123"},json=payload)
    second=client.post("/api/gateway/execute",headers={"Idempotency-Key":"order-123"},json=payload)
    assert first.status_code==second.status_code==200
    assert second.headers["x-guard-replayed"]=="true"
    assert mock_upstream.await_count==1
