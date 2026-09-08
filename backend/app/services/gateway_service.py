from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse
from uuid import UUID

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import NotFoundError, UpstreamError
from app.core.security import path_for_policy_match, validate_relative_path
from app.models.agent import Agent
from app.models.policy import Decision, Policy, RiskLevel
from app.schemas.gateway import GatewayExecuteRequest
from app.services import event_service, approval_service, audit_service
from app.services.policy_engine import find_matching_policy

NO_POLICY_REASON = "No matching security policy found"
INACTIVE_AGENT_REASON = "Agent is inactive"
ALLOW_REASON = "Request allowed by matched security policy"


@dataclass
class GatewayOutcome:
    status_code: int
    payload: dict[str, Any]


def _upstream_base() -> str:
    return str(settings.DEMOSHOP_BASE_URL).rstrip("/")


def _assert_url_stays_on_upstream(url: str) -> None:
    base = urlparse(_upstream_base())
    target = urlparse(url)
    if target.scheme != base.scheme or target.netloc != base.netloc:
        raise UpstreamError("Refusing to forward request outside the configured DemoShop upstream", 400)


async def forward_to_demoshop(method: str, path: str, body: Any | None) -> httpx.Response:
    timeout = httpx.Timeout(settings.UPSTREAM_TIMEOUT_SECONDS)
    async with httpx.AsyncClient(
        base_url=_upstream_base(),
        timeout=timeout,
        follow_redirects=False,
    ) as client:
        kwargs: dict[str, Any] = {}
        if body is not None:
            kwargs["json"] = body
        request = client.build_request(method, path, **kwargs)
        _assert_url_stays_on_upstream(str(request.url))
        return await client.send(request)


def _get_agent_by_slug(db: Session, slug: str) -> Agent:
    agent = db.query(Agent).filter(Agent.slug == slug).first()
    if agent is None:
        raise NotFoundError(f"Agent '{slug}' not found")
    return agent


def _parse_upstream_body(response: httpx.Response) -> Any:
    content_type = response.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            return response.json()
        except ValueError:
            return response.text
    return response.text


def _build_response(
    *,
    decision: Decision,
    risk_level: RiskLevel,
    reason: str,
    matched_policy_id: UUID | None = None,
    upstream_status: int | None = None,
    data: Any | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "decision": decision.value,
        "risk_level": risk_level.value,
        "reason": reason,
        "matched_policy_id": str(matched_policy_id) if matched_policy_id else None,
        "data": data,
    }
    if upstream_status is not None:
        payload["upstream_status"] = upstream_status
    return payload


def _record(
    db: Session,
    agent: Agent,
    payload: GatewayExecuteRequest,
    path: str,
    decision: Decision,
    risk_level: RiskLevel,
    reason: str,
    policy: Policy | None,
) -> Any:
    return event_service.record_event(
        db,
        agent_id=agent.id,
        method=payload.method.value,
        path=path,
        decision=decision,
        risk_level=risk_level,
        reason=reason,
        matched_policy_id=None if policy is None else policy.id,
        request_body=payload.body,
        organization_id=agent.organization_id,
    )


async def execute(db: Session, payload: GatewayExecuteRequest) -> GatewayOutcome:
    agent = _get_agent_by_slug(db, payload.agent)
    path = validate_relative_path(payload.path)
    method = payload.method.value

    if not agent.active:
        _record(
            db,
            agent,
            payload,
            path,
            Decision.BLOCK,
            RiskLevel.HIGH,
            INACTIVE_AGENT_REASON,
            None,
        )
        return GatewayOutcome(
            status_code=403,
            payload=_build_response(
                decision=Decision.BLOCK,
                risk_level=RiskLevel.HIGH,
                reason=INACTIVE_AGENT_REASON,
            ),
        )

    policy = find_matching_policy(db, agent.id, method, path_for_policy_match(path))
    if policy is None:
        _record(
            db,
            agent,
            payload,
            path,
            Decision.BLOCK,
            RiskLevel.HIGH,
            NO_POLICY_REASON,
            None,
        )
        return GatewayOutcome(
            status_code=403,
            payload=_build_response(
                decision=Decision.BLOCK,
                risk_level=RiskLevel.HIGH,
                reason=NO_POLICY_REASON,
            ),
        )

    recorded_event = _record(
        db,
        agent,
        payload,
        path,
        policy.decision,
        policy.risk_level,
        policy.description,
        policy,
    )

    if policy.decision == Decision.BLOCK:
        return GatewayOutcome(
            status_code=403,
            payload=_build_response(
                decision=policy.decision,
                risk_level=policy.risk_level,
                reason=policy.description,
                matched_policy_id=policy.id,
            ),
        )

    if policy.decision == Decision.REQUIRE_APPROVAL:
        approval = approval_service.create_for_event(db, recorded_event)
        audit_service.append_audit_log(db, actor=agent.slug, action="approval.requested", resource_type="approval_request", resource_id=str(approval.id), organization_id=agent.organization_id, details={"path": path, "risk": policy.risk_level.value})
        return GatewayOutcome(
            status_code=202,
            payload=_build_response(
                decision=policy.decision,
                risk_level=policy.risk_level,
                reason=policy.description,
                matched_policy_id=policy.id,
            ),
        )

    try:
        upstream = await forward_to_demoshop(method, path, payload.body)
    except httpx.TimeoutException as exc:
        raise UpstreamError("DemoShop API request timed out", 503) from exc
    except httpx.RequestError as exc:
        raise UpstreamError("DemoShop API is unreachable", 502) from exc

    return GatewayOutcome(
        status_code=200,
        payload=_build_response(
            decision=Decision.ALLOW,
            risk_level=policy.risk_level,
            reason=ALLOW_REASON,
            matched_policy_id=policy.id,
            upstream_status=upstream.status_code,
            data=_parse_upstream_body(upstream),
        ),
    )
