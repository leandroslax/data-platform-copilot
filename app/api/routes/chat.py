from fastapi import APIRouter

from app.api.schemas.chat import ChatRequest, ChatResponse
from app.api.services.chat_service import answer_question

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    return answer_question(payload.question)
