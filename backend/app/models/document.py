from pydantic import BaseModel
from typing import Optional


class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    uploaded_at: str
    chunk_count: Optional[int] = None
