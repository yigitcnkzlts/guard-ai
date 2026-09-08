from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.gateway import GatewayExecuteRequest, GatewayExecuteResponse
from app.services import gateway_service
from app.core.config import settings
from app.core.gateway_guard import IdempotencyStore, RateLimiter

_rate_limiter = RateLimiter(settings.GATEWAY_RATE_LIMIT, 60)
_idempotency = IdempotencyStore()

router = APIRouter(prefix="/gateway", tags=["gateway"])


@router.post("/execute", response_model=GatewayExecuteResponse)
async def execute_gateway(
    payload: GatewayExecuteRequest,
    request: Request,
    db: Session = Depends(get_db),
    x_guard_api_key: str | None = Header(default=None),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> JSONResponse:
    if settings.GATEWAY_API_KEY and x_guard_api_key != settings.GATEWAY_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid GUARD API key")
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > settings.MAX_REQUEST_BODY_BYTES:
                raise HTTPException(status_code=413, detail="Request body is too large")
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid Content-Length header") from exc
    client_key = f"{request.client.host if request.client else 'unknown'}:{payload.agent}"
    if not _rate_limiter.allow(client_key):
        raise HTTPException(status_code=429, detail="Gateway rate limit exceeded")
    cache_key = f"{payload.agent}:{idempotency_key}" if idempotency_key else None
    if cache_key:
        cached = _idempotency.get(cache_key)
        if cached is not None:
            return JSONResponse(status_code=cached.status_code, content=cached.payload, headers={"X-GUARD-Replayed": "true"})
    outcome = await gateway_service.execute(db, payload)
    if cache_key:
        _idempotency.put(cache_key, outcome)
    return JSONResponse(status_code=outcome.status_code, content=outcome.payload)
