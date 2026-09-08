"""Dashboard API endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.dashboard import DashboardSummary
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    days: int = Query(default=7, ge=1, le=90),
) -> DashboardSummary:
    """Get dashboard summary metrics for the last N days."""
    total_requests = dashboard_service.get_total_requests(db, days)
    allowed_requests = dashboard_service.get_allowed_requests(db, days)
    blocked_requests = dashboard_service.get_blocked_requests(db, days)
    critical_risks = len(dashboard_service.get_critical_risk_events(db, days))
    active_agents = len(dashboard_service.get_active_agents(db))
    block_rate = dashboard_service.get_block_rate(db, days)
    requests_by_risk_level = dashboard_service.get_requests_by_risk_level(db, days)
    requests_by_decision = dashboard_service.get_requests_by_decision(db, days)
    requests_by_agent = dashboard_service.get_requests_by_agent(db, days)
    
    return DashboardSummary(
        total_requests=total_requests,
        allowed_requests=allowed_requests,
        blocked_requests=blocked_requests,
        block_rate=block_rate,
        critical_risks=critical_risks,
        active_agents=active_agents,
        requests_by_risk_level=requests_by_risk_level,
        requests_by_decision=requests_by_decision,
        requests_by_agent=requests_by_agent,
    )
