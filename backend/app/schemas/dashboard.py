"""Dashboard schemas for API responses."""

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    """Dashboard summary metrics."""
    
    total_requests: int
    allowed_requests: int
    blocked_requests: int
    block_rate: float  # percentage
    critical_risks: int
    active_agents: int
    requests_by_risk_level: dict[str, int]
    requests_by_decision: dict[str, int]
    requests_by_agent: dict[str, int]
