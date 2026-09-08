from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api import api_router
from app.core.exceptions import AppError
from app.models import Customer, Order  # noqa: F401

app = FastAPI(
    title="DemoShop API",
    description="Sample e-commerce API used to test the GUARD AI runtime security gateway.",
    version="0.1.0",
)

app.include_router(api_router)


@app.exception_handler(AppError)
async def handle_app_error(_request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})
