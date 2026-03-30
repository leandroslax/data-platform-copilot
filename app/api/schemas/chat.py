from typing import List

from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str


class ChatSource(BaseModel):
    type: str
    id: str
    label: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[ChatSource]
