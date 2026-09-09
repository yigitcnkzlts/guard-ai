from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from uuid import uuid4
from contextlib import asynccontextmanager

from app.api import api_router
from app.core.config import settings
from app.core.exceptions import AppError
from app.database.bootstrap import bootstrap_database
from app.models import Agent, ApprovalRequest, AuditLog, Organization, Policy, SecurityEvent  # noqa: F401
from app.services import metrics_service
from app.services.gateway_service import close_http_client

@asynccontextmanager
async def lifespan(_app: FastAPI):
    bootstrap_database()
    yield
    await close_http_client()

app = FastAPI(
    title="GUARD AI",
    description="Runtime security gateway and policy engine for AI agent API actions.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)

app.include_router(api_router)

@app.middleware("http")
async def security_and_observability_headers(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid4()))[:128]
    request.state.request_id = request_id
    started = time.perf_counter()
    response = await call_next(request)
    latency_ms=(time.perf_counter()-started)*1000
    metrics_service.observe(request.method,request.url.path,response.status_code,latency_ms)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-Ms"] = f"{latency_ms:.2f}"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


@app.exception_handler(AppError)
async def handle_app_error(_request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"code": exc.code, "message": exc.message, "request_id": getattr(_request.state, "request_id", None), "details": exc.details, "detail": exc.message})

@app.exception_handler(HTTPException)
async def handle_http_error(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"code": f"HTTP_{exc.status_code}", "message": str(exc.detail), "request_id": getattr(request.state, "request_id", None), "details": {}, "detail": exc.detail})

@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"code": "VALIDATION_ERROR", "message": "Request validation failed", "request_id": getattr(request.state, "request_id", None), "details": {"errors": exc.errors()}, "detail": exc.errors()})
