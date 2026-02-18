from pydantic import BaseModel
from typing import Optional


class NoteCreate(BaseModel):
    title: str
    category: Optional[str] = None
    content: str


class NoteResponse(BaseModel):
    id: str
    title: str
    category: Optional[str] = None
    created_at: str
    updated_at: str
