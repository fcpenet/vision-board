from pydantic import BaseModel
from typing import Optional
from enum import Enum


class ChecklistStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    done = "done"


class ChecklistItemCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: str
    status: ChecklistStatus = ChecklistStatus.pending
    due_date: Optional[str] = None


class ChecklistItemUpdate(BaseModel):
    status: ChecklistStatus


class ChecklistItemResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    category: str
    status: str
    due_date: Optional[str] = None
    created_at: str
    updated_at: str
