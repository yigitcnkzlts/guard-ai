from fastapi import APIRouter
from app.services.metrics_service import snapshot
router=APIRouter(tags=["operations"])
@router.get("/metrics")
def metrics()->dict: return snapshot()
