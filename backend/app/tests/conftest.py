import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport
from app.main import app


# ---------------------------------------------------------------------------
# Shared mock data helpers
# ---------------------------------------------------------------------------

def make_turso_row(*values):
    """Wrap values so they behave like a libsql_client row (index-accessible)."""
    return values


def make_turso_result(rows):
    result = MagicMock()
    result.rows = rows
    return result


# ---------------------------------------------------------------------------
# App client fixture
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# Patch fixtures — external I/O
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def mock_turso(monkeypatch):
    """Replace turso.execute with an AsyncMock; tests override return_value as needed."""
    mock = AsyncMock(return_value=make_turso_result([]))
    monkeypatch.setattr("app.db.turso.execute", mock)
    monkeypatch.setattr("app.db.turso.init_db", AsyncMock())
    return mock


@pytest.fixture(autouse=True)
def mock_vector_store(monkeypatch):
    mocks = {
        "upsert": MagicMock(),
        "delete": MagicMock(),
        "query": MagicMock(return_value={"documents": [[]], "metadatas": [[]], "distances": [[]]}),
    }
    monkeypatch.setattr("app.db.vector_store.upsert_chunks", mocks["upsert"])
    monkeypatch.setattr("app.db.vector_store.delete_by_source", mocks["delete"])
    monkeypatch.setattr("app.db.vector_store.query_chunks", mocks["query"])
    # Also patch within routes/services that imported directly
    monkeypatch.setattr("app.api.routes.notes.upsert_chunks", mocks["upsert"])
    monkeypatch.setattr("app.api.routes.notes.delete_by_source", mocks["delete"])
    monkeypatch.setattr("app.api.routes.documents.upsert_chunks", mocks["upsert"])
    monkeypatch.setattr("app.api.routes.documents.delete_by_source", mocks["delete"])
    monkeypatch.setattr("app.services.rag_service.query_chunks", mocks["query"])
    return mocks


@pytest.fixture(autouse=True)
def mock_embedding(monkeypatch):
    embedding = [0.1] * 1536
    mock_embed = AsyncMock(return_value=embedding)
    mock_embed_many = AsyncMock(return_value=[embedding])
    monkeypatch.setattr("app.services.embedding_service.embed", mock_embed)
    monkeypatch.setattr("app.services.embedding_service.embed_many", mock_embed_many)
    monkeypatch.setattr("app.api.routes.notes.embed", mock_embed)
    monkeypatch.setattr("app.api.routes.documents.embed_many", mock_embed_many)
    monkeypatch.setattr("app.services.rag_service.embed", mock_embed)
    return {"embed": mock_embed, "embed_many": mock_embed_many}


@pytest.fixture(autouse=True)
def mock_chat_complete(monkeypatch):
    mock = AsyncMock(return_value="This is a test answer.")
    monkeypatch.setattr("app.services.chat_service.complete", mock)
    monkeypatch.setattr("app.services.rag_service.complete", mock)
    return mock
