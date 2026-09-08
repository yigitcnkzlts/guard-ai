from fastapi import APIRouter

from app.api.agents import router as agents_router
from app.api.dashboard import router as dashboard_router
from app.api.events import router as events_router
from app.api.gateway import router as gateway_router
from app.api.health import router as health_router
from app.api.policies import router as policies_router
from app.api.approvals import router as approvals_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(gateway_router, prefix="/api")
api_router.include_router(agents_router, prefix="/api")
api_router.include_router(policies_router, prefix="/api")
api_router.include_router(events_router, prefix="/api")
api_router.include_router(dashboard_router, prefix="/api")
api_router.include_router(approvals_router, prefix="/api")
