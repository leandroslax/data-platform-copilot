from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


@router.post("/chat")
def chat(payload: ChatRequest) -> dict:
    return {
        "answer": f"Question received: {payload.question}",
        "sources": [],
    }
