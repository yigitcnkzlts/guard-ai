from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import settings
from app.core.exceptions import GuardUnavailableError


@dataclass
class GuardResponse:
    status_code: int
    body: Any
    raw_text: str


class GuardClient:
    """All business actions must go through the GUARD Security Gateway."""

    def execute(self, method: str, path: str, body: Any | None = None) -> GuardResponse:
        url = f"{settings.GUARD_API_URL.rstrip('/')}/api/gateway/execute"
        payload = {
            "agent": "customer-support-agent",
            "method": method,
            "path": path,
            "body": body,
        }

        try:
            with httpx.Client(timeout=settings.GUARD_TIMEOUT_SECONDS) as client:
                response = client.post(url, json=payload)
        except httpx.TimeoutException as exc:
            raise GuardUnavailableError("GUARD security gateway request timed out") from exc
        except httpx.RequestError as exc:
            raise GuardUnavailableError("GUARD security gateway is unavailable") from exc

        raw_text = response.text
        parsed: Any
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            try:
                parsed = response.json()
            except ValueError:
                parsed = raw_text
        else:
            parsed = raw_text

        return GuardResponse(status_code=response.status_code, body=parsed, raw_text=raw_text)
