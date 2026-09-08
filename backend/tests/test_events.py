from datetime import datetime, timedelta, timezone

import pytest

from app.models.agent import Agent
from app.models.policy import Decision, RiskLevel
from app.models.security_event import SecurityEvent


def seed_events(db, count=205):
    agent = db.query(Agent).first()
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    rows = [SecurityEvent(
        agent_id=agent.id, method="POST", path=f"/api/orders/{i}",
        decision=Decision.BLOCK, risk_level=RiskLevel.HIGH,
        reason="Unmatched request", created_at=start + timedelta(seconds=i),
    ) for i in range(count)]
    rows[0].reason = "Special 100%_Refund"
    db.add_all(rows)
    db.commit()
    return rows


def test_search_finds_events_beyond_latest_200(client, db_session):
    rows = seed_events(db_session)
    response = client.get("/api/security-events", params={"search": "  refund  "})
    assert response.status_code == 200
    assert [row["id"] for row in response.json()] == [str(rows[0].id)]


def test_pagination_and_combined_filters(client, db_session):
    rows = seed_events(db_session, 6)
    params = {"limit": 2, "decision": "BLOCK", "risk_level": "HIGH",
              "agent_id": str(rows[0].agent_id), "search": "/api/orders/"}
    first = client.get("/api/security-events", params=params).json()
    second = client.get("/api/security-events", params={**params, "offset": 2}).json()
    assert [row["id"] for row in first + second] == [str(row.id) for row in reversed(rows[2:])]
    assert client.get("/api/security-events", params={**params, "decision": "ALLOW"}).json() == []
    assert client.get("/api/security-events", params={"offset": 6}).json() == []


@pytest.mark.parametrize("term", ["%", "_", "100%_", "Special"])
def test_search_treats_wildcards_as_literal_text(client, db_session, term):
    rows = seed_events(db_session, 3)
    result = client.get("/api/security-events", params={"search": term})
    assert result.status_code == 200
    assert [row["id"] for row in result.json()] == [str(rows[0].id)]


@pytest.mark.parametrize("params", [{"offset": -1}, {"limit": 201}, {"search": "a" * 201}])
def test_invalid_event_query_is_rejected(client, params):
    assert client.get("/api/security-events", params=params).status_code == 422
