from sqlalchemy.orm import Session

from app.models.agent import Agent, AgentEnvironment
from app.models.policy import Decision, Policy, RiskLevel

CUSTOMER_SUPPORT_SLUG = "customer-support-agent"
FINANCE_AGENT_SLUG = "finance-agent"
DEVELOPER_AGENT_SLUG = "developer-agent"

# Customer Support Agent policies
CUSTOMER_SUPPORT_POLICIES: list[dict[str, str | Decision | RiskLevel]] = [
    {
        "name": "List orders",
        "method": "GET",
        "path_pattern": "/api/orders",
        "decision": Decision.ALLOW,
        "risk_level": RiskLevel.LOW,
        "description": "Order listing is allowed",
    },
    {
        "name": "Get order by id",
        "method": "GET",
        "path_pattern": "/api/orders/{order_id}",
        "decision": Decision.ALLOW,
        "risk_level": RiskLevel.LOW,
        "description": "Order lookup is allowed",
    },
    {
        "name": "Cancel a single order",
        "method": "POST",
        "path_pattern": "/api/orders/{order_id}/cancel",
        "decision": Decision.ALLOW,
        "risk_level": RiskLevel.MEDIUM,
        "description": "Single order cancellation is allowed",
    },
    {
        "name": "Refund an order",
        "method": "POST",
        "path_pattern": "/api/orders/{order_id}/refund",
        "decision": Decision.REQUIRE_APPROVAL,
        "risk_level": RiskLevel.HIGH,
        "description": "Refund operations require human approval",
    },
    {
        "name": "Cancel all orders",
        "method": "POST",
        "path_pattern": "/api/orders/cancel-all",
        "decision": Decision.BLOCK,
        "risk_level": RiskLevel.CRITICAL,
        "description": "Bulk order cancellation is prohibited by security policy",
    },
]

# Finance Agent policies
FINANCE_AGENT_POLICIES: list[dict[str, str | Decision | RiskLevel]] = [
    {
        "name": "View financial data",
        "method": "GET",
        "path_pattern": "/api/financial",
        "decision": Decision.ALLOW,
        "risk_level": RiskLevel.LOW,
        "description": "Financial data read access is allowed",
    },
    {
        "name": "View transaction history",
        "method": "GET",
        "path_pattern": "/api/transactions",
        "decision": Decision.ALLOW,
        "risk_level": RiskLevel.LOW,
        "description": "Transaction history access is allowed",
    },
    {
        "name": "Record financial transactions",
        "method": "POST",
        "path_pattern": "/api/transactions",
        "decision": Decision.ALLOW,
        "risk_level": RiskLevel.MEDIUM,
        "description": "Transaction recording is allowed for financial agent",
    },
    {
        "name": "Modify sensitive financial data",
        "method": "PUT",
        "path_pattern": "/api/financial/settings",
        "decision": Decision.REQUIRE_APPROVAL,
        "risk_level": RiskLevel.CRITICAL,
        "description": "Financial settings changes require approval",
    },
]

# Developer Agent policies
DEVELOPER_AGENT_POLICIES: list[dict[str, str | Decision | RiskLevel]] = [
    {
        "name": "Read GitHub repositories",
        "method": "GET",
        "path_pattern": "/api/github/repos",
        "decision": Decision.ALLOW,
        "risk_level": RiskLevel.LOW,
        "description": "GitHub repository read access is allowed",
    },
    {
        "name": "Read production secrets",
        "method": "GET",
        "path_pattern": "/api/secrets/production",
        "decision": Decision.BLOCK,
        "risk_level": RiskLevel.CRITICAL,
        "description": "Production secrets access is blocked for developer agents",
    },
    {
        "name": "Read staging secrets",
        "method": "GET",
        "path_pattern": "/api/secrets/staging",
        "decision": Decision.ALLOW,
        "risk_level": RiskLevel.MEDIUM,
        "description": "Staging secrets access is allowed",
    },
    {
        "name": "Deploy to staging",
        "method": "POST",
        "path_pattern": "/api/deployments/staging",
        "decision": Decision.ALLOW,
        "risk_level": RiskLevel.MEDIUM,
        "description": "Staging deployment is allowed",
    },
    {
        "name": "Deploy to production",
        "method": "POST",
        "path_pattern": "/api/deployments/production",
        "decision": Decision.BLOCK,
        "risk_level": RiskLevel.CRITICAL,
        "description": "Production deployment is blocked for developer agents",
    },
]


def seed_agent_with_policies(
    db: Session,
    agent_slug: str,
    agent_name: str,
    agent_description: str,
    policies: list[dict[str, str | Decision | RiskLevel]],
) -> Agent:
    """Seed an agent with its associated policies."""
    agent = db.query(Agent).filter(Agent.slug == agent_slug).first()
    if agent is None:
        agent = Agent(
            name=agent_name,
            slug=agent_slug,
            description=agent_description,
            environment=AgentEnvironment.DEVELOPMENT,
            active=True,
        )
        db.add(agent)
        db.flush()

    existing = {
        (policy.method, policy.path_pattern)
        for policy in db.query(Policy).filter(Policy.agent_id == agent.id).all()
    }
    for spec in policies:
        key = (str(spec["method"]), str(spec["path_pattern"]))
        if key in existing:
            continue
        db.add(
            Policy(
                name=str(spec["name"]),
                agent_id=agent.id,
                method=str(spec["method"]),
                path_pattern=str(spec["path_pattern"]),
                decision=spec["decision"],
                risk_level=spec["risk_level"],
                description=str(spec["description"]),
                active=True,
            )
        )
    db.commit()
    db.refresh(agent)
    return agent


def seed_customer_support_agent(db: Session) -> Agent:
    return seed_agent_with_policies(
        db,
        CUSTOMER_SUPPORT_SLUG,
        "Customer Support Agent",
        "Handles customer support actions against DemoShop APIs.",
        CUSTOMER_SUPPORT_POLICIES,
    )


def seed_finance_agent(db: Session) -> Agent:
    return seed_agent_with_policies(
        db,
        FINANCE_AGENT_SLUG,
        "Finance Agent",
        "Handles financial operations and transaction management.",
        FINANCE_AGENT_POLICIES,
    )


def seed_developer_agent(db: Session) -> Agent:
    return seed_agent_with_policies(
        db,
        DEVELOPER_AGENT_SLUG,
        "Developer Agent",
        "Manages development and staging deployments.",
        DEVELOPER_AGENT_POLICIES,
    )
