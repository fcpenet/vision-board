import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from app.models.note import NoteCreate, NoteResponse
from app.db import turso
from app.db.vector_store import upsert_chunks, delete_by_source
from app.services.embedding_service import embed

router = APIRouter(prefix="/api/notes", tags=["notes"])


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.post("", status_code=201, response_model=NoteResponse)
async def create_note(body: NoteCreate) -> NoteResponse:
    note_id = str(uuid.uuid4())
    now = _now()

    await turso.execute(
        "INSERT INTO notes (id, title, category, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        [note_id, body.title, body.category, now, now],
    )

    embedding = await embed(body.content)
    upsert_chunks(
        ids=[f"{note_id}_0"],
        documents=[body.content],
        embeddings=[embedding],
        metadatas=[{"source_id": note_id, "source_type": "note", "title": body.title, "category": body.category or ""}],
    )

    return NoteResponse(id=note_id, title=body.title, category=body.category, created_at=now, updated_at=now)


@router.get("", response_model=list[NoteResponse])
async def list_notes() -> list[NoteResponse]:
    result = await turso.execute("SELECT id, title, category, created_at, updated_at FROM notes ORDER BY created_at DESC")
    return [
        NoteResponse(id=row[0], title=row[1], category=row[2], created_at=row[3], updated_at=row[4])
        for row in result.rows
    ]


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(note_id: str) -> NoteResponse:
    result = await turso.execute(
        "SELECT id, title, category, created_at, updated_at FROM notes WHERE id = ?",
        [note_id],
    )
    if not result.rows:
        raise HTTPException(status_code=404, detail="Note not found")
    row = result.rows[0]
    return NoteResponse(id=row[0], title=row[1], category=row[2], created_at=row[3], updated_at=row[4])


@router.delete("/{note_id}", status_code=204)
async def delete_note(note_id: str) -> None:
    result = await turso.execute("SELECT id FROM notes WHERE id = ?", [note_id])
    if not result.rows:
        raise HTTPException(status_code=404, detail="Note not found")
    await turso.execute("DELETE FROM notes WHERE id = ?", [note_id])
    delete_by_source(note_id)
