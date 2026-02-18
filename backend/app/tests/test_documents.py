import io
import pytest
from unittest.mock import MagicMock, patch
from .conftest import make_turso_result, make_turso_row

pytestmark = pytest.mark.asyncio

DOC_ROW = make_turso_row(
    "doc-id-1", "dnv_guide.pdf", "pdf",
    "2024-01-01T00:00:00+00:00", 3,
)

FAKE_PDF_TEXT = "This is a test PDF document about the Spain Digital Nomad Visa requirements."


def make_fake_pdf_bytes() -> bytes:
    """Return minimal valid PDF bytes using fitz/PyMuPDF."""
    import fitz
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), FAKE_PDF_TEXT)
    return doc.tobytes()


@pytest.fixture
def pdf_bytes():
    return make_fake_pdf_bytes()


async def test_upload_pdf_returns_200(client, pdf_bytes):
    resp = await client.post(
        "/api/documents/upload",
        files={"file": ("dnv_guide.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )
    assert resp.status_code == 200


async def test_upload_pdf_stores_metadata_in_turso(client, mock_turso, pdf_bytes):
    await client.post(
        "/api/documents/upload",
        files={"file": ("dnv_guide.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )
    call_sql = mock_turso.call_args_list[0][0][0]
    assert "INSERT INTO documents" in call_sql


async def test_upload_pdf_chunks_and_stores_embeddings_in_chromadb(client, mock_vector_store, mock_embedding, pdf_bytes):
    await client.post(
        "/api/documents/upload",
        files={"file": ("dnv_guide.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )
    mock_embedding["embed_many"].assert_called_once()
    mock_vector_store["upsert"].assert_called_once()


async def test_upload_non_pdf_returns_400(client):
    resp = await client.post(
        "/api/documents/upload",
        files={"file": ("notes.txt", io.BytesIO(b"plain text"), "text/plain")},
    )
    assert resp.status_code == 400


async def test_uploaded_doc_is_queryable_via_chat(client, mock_vector_store, pdf_bytes):
    doc_meta = {"source_id": "doc-id-1", "source_type": "document", "title": "dnv_guide.pdf", "category": "document"}
    mock_vector_store["query"].return_value = {
        "documents": [[FAKE_PDF_TEXT]],
        "metadatas": [[doc_meta]],
        "distances": [[0.05]],
    }
    resp = await client.post("/api/chat", json={"query": "DNV requirements"})
    assert resp.status_code == 200
    assert "doc-id-1" in resp.json()["sources"]


async def test_chunk_count_stored_in_turso(client, mock_turso, pdf_bytes):
    await client.post(
        "/api/documents/upload",
        files={"file": ("dnv_guide.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )
    insert_args = mock_turso.call_args_list[0][0][1]
    chunk_count = insert_args[4]
    assert chunk_count >= 1
