"""Dashboard metrics and summary service."""

from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.policy import Decision, RiskLevel
from app.models.security_event import SecurityEvent


def get_total_requests(db: Session, days: int = 7) -> int:
    """Get total requests in last N days."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    count = (
        db.query(func.count(SecurityEvent.id))
        .filter(SecurityEvent.created_at >= cutoff)
        .scalar()
    )
    return count or 0


def get_allowed_requests(db: Session, days: int = 7) -> int:
    """Get allowed requests in last N days."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    count = (
        db.query(func.count(SecurityEvent.id))
        .filter(
            and_(
                SecurityEvent.created_at >= cutoff,
                SecurityEvent.decision == Decision.ALLOW,
            )
        )
        .scalar()
    )
    return count or 0


def get_blocked_requests(db: Session, days: int = 7) -> int:
    """Get blocked requests in last N days."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    count = (
        db.query(func.count(SecurityEvent.id))
        .filter(
            and_(
                SecurityEvent.created_at >= cutoff,
                SecurityEvent.decision == Decision.BLOCK,
            )
        )
        .scalar()
    )
    return count or 0


def get_critical_risk_events(db: Session, days: int = 7, limit: int = 10) -> list[SecurityEvent]:
    """Get critical risk events in last N days."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    return (
        db.query(SecurityEvent)
        .filter(
            and_(
                SecurityEvent.created_at >= cutoff,
                SecurityEvent.risk_level == RiskLevel.CRITICAL,
            )
        )
        .order_by(SecurityEvent.created_at.desc())
        .limit(limit)
        .all()
    )


def get_active_agents(db: Session) -> list[Agent]:
    """Get all active agents."""
    return db.query(Agent).filter(Agent.active.is_(True)).all()


def get_block_rate(db: Session, days: int = 7) -> float:
    """Get block rate percentage in last N days."""
    total = get_total_requests(db, days)
    if total == 0:
        return 0.0
    blocked = get_blocked_requests(db, days)
    return round((blocked / total) * 100, 2)


def get_requests_by_risk_level(db: Session, days: int = 7) -> dict[str, int]:
    """Get request count by risk level in last N days."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    results = (
        db.query(SecurityEvent.risk_level, func.count(SecurityEvent.id))
        .filter(SecurityEvent.created_at >= cutoff)
        .group_by(SecurityEvent.risk_level)
        .all()
    )
    return {risk_level.value: count for risk_level, count in results}


def get_requests_by_decision(db: Session, days: int = 7) -> dict[str, int]:
    """Get request count by decision in last N days."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    results = (
        db.query(SecurityEvent.decision, func.count(SecurityEvent.id))
        .filter(SecurityEvent.created_at >= cutoff)
        .group_by(SecurityEvent.decision)
        .all()
    )
    return {decision.value: count for decision, count in results}


def get_requests_by_agent(db: Session, days: int = 7) -> dict[str, int]:
    """Get request count by agent in last N days."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    results = (
        db.query(Agent.name, func.count(SecurityEvent.id))
        .join(SecurityEvent, Agent.id == SecurityEvent.agent_id)
        .filter(SecurityEvent.created_at >= cutoff)
        .group_by(Agent.name)
        .all()
    )
    return {name: count for name, count in results}
