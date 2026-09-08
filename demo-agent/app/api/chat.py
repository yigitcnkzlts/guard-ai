from fastapi import APIRouter

from app.agent.customer_support import analyze_message
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    return analyze_message(payload.message)
