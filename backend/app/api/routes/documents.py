import uuid
import math
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, UploadFile, File
import fitz
from app.models.document import DocumentResponse
from app.db import turso
from app.db.vector_store import upsert_chunks, delete_by_source
from app.services.embedding_service import embed_many

router = APIRouter(prefix="/api/documents", tags=["documents"])

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    words = text.split()
    chunks = []
    step = chunk_size - overlap
    for i in range(0, max(1, len(words)), step):
        chunk = " ".join(words[i: i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...)) -> DocumentResponse:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    doc_id = str(uuid.uuid4())
    now = _now()
    content = await file.read()

    pdf = fitz.open(stream=content, filetype="pdf")
    full_text = "\n".join(page.get_text() for page in pdf)
    pdf.close()

    chunks = _chunk_text(full_text)
    embeddings = await embed_many(chunks)

    chunk_ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
    metadatas = [
        {"source_id": doc_id, "source_type": "document", "title": file.filename, "category": "document"}
        for _ in chunks
    ]
    upsert_chunks(chunk_ids, chunks, embeddings, metadatas)

    await turso.execute(
        "INSERT INTO documents (id, filename, file_type, uploaded_at, chunk_count) VALUES (?, ?, ?, ?, ?)",
        [doc_id, file.filename, "pdf", now, len(chunks)],
    )

    return DocumentResponse(id=doc_id, filename=file.filename, file_type="pdf", uploaded_at=now, chunk_count=len(chunks))


@router.get("", response_model=list[DocumentResponse])
async def list_documents() -> list[DocumentResponse]:
    result = await turso.execute(
        "SELECT id, filename, file_type, uploaded_at, chunk_count FROM documents ORDER BY uploaded_at DESC"
    )
    return [
        DocumentResponse(id=row[0], filename=row[1], file_type=row[2], uploaded_at=row[3], chunk_count=row[4])
        for row in result.rows
    ]


@router.delete("/{doc_id}", status_code=204)
async def delete_document(doc_id: str) -> None:
    result = await turso.execute("SELECT id FROM documents WHERE id = ?", [doc_id])
    if not result.rows:
        raise HTTPException(status_code=404, detail="Document not found")
    await turso.execute("DELETE FROM documents WHERE id = ?", [doc_id])
    delete_by_source(doc_id)
