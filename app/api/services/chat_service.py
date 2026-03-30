from app.api.schemas.chat import ChatResponse


def answer_question(question: str) -> ChatResponse:
    return ChatResponse(
        answer=f"Question received: {question}",
        sources=[],
    )
