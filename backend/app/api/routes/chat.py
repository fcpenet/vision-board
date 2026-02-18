from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag_service import chat

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]


@router.post("", response_model=ChatResponse)
async def chat_endpoint(body: ChatRequest) -> ChatResponse:
    if not body.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    result = await chat(body.query)
    return ChatResponse(answer=result["answer"], sources=result["sources"])
