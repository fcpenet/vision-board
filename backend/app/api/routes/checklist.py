import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from typing import Optional
from app.models.checklist import ChecklistItemCreate, ChecklistItemUpdate, ChecklistItemResponse
from app.db import turso

router = APIRouter(prefix="/api/checklist", tags=["checklist"])


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.get("", response_model=list[ChecklistItemResponse])
async def list_items(category: Optional[str] = None) -> list[ChecklistItemResponse]:
    if category:
        result = await turso.execute(
            "SELECT id, title, description, category, status, due_date, created_at, updated_at FROM checklist_items WHERE category = ? ORDER BY created_at DESC",
            [category],
        )
    else:
        result = await turso.execute(
            "SELECT id, title, description, category, status, due_date, created_at, updated_at FROM checklist_items ORDER BY created_at DESC"
        )
    return [
        ChecklistItemResponse(
            id=row[0], title=row[1], description=row[2], category=row[3],
            status=row[4], due_date=row[5], created_at=row[6], updated_at=row[7],
        )
        for row in result.rows
    ]


@router.post("", status_code=201, response_model=ChecklistItemResponse)
async def create_item(body: ChecklistItemCreate) -> ChecklistItemResponse:
    item_id = str(uuid.uuid4())
    now = _now()
    await turso.execute(
        "INSERT INTO checklist_items (id, title, description, category, status, due_date, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        [item_id, body.title, body.description, body.category, body.status.value, body.due_date, now, now],
    )
    return ChecklistItemResponse(
        id=item_id, title=body.title, description=body.description,
        category=body.category, status=body.status.value,
        due_date=body.due_date, created_at=now, updated_at=now,
    )


@router.patch("/{item_id}", response_model=ChecklistItemResponse)
async def update_item_status(item_id: str, body: ChecklistItemUpdate) -> ChecklistItemResponse:
    result = await turso.execute(
        "SELECT id, title, description, category, status, due_date, created_at, updated_at FROM checklist_items WHERE id = ?",
        [item_id],
    )
    if not result.rows:
        raise HTTPException(status_code=404, detail="Item not found")
    now = _now()
    await turso.execute(
        "UPDATE checklist_items SET status = ?, updated_at = ? WHERE id = ?",
        [body.status.value, now, item_id],
    )
    row = result.rows[0]
    return ChecklistItemResponse(
        id=row[0], title=row[1], description=row[2], category=row[3],
        status=body.status.value, due_date=row[5], created_at=row[6], updated_at=now,
    )


@router.delete("/{item_id}", status_code=204)
async def delete_item(item_id: str) -> None:
    result = await turso.execute("SELECT id FROM checklist_items WHERE id = ?", [item_id])
    if not result.rows:
        raise HTTPException(status_code=404, detail="Item not found")
    await turso.execute("DELETE FROM checklist_items WHERE id = ?", [item_id])
