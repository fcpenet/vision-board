import pytest
from .conftest import make_turso_result, make_turso_row

pytestmark = pytest.mark.asyncio


NOTE_ROW = make_turso_row(
    "note-id-1", "Why Alicante", "decisions",
    "2024-01-01T00:00:00+00:00", "2024-01-01T00:00:00+00:00"
)


async def test_create_note_returns_201(client, mock_turso):
    resp = await client.post("/api/notes", json={"title": "Why Alicante", "category": "decisions", "content": "320 sunny days"})
    assert resp.status_code == 201


async def test_create_note_stores_metadata_in_turso(client, mock_turso):
    await client.post("/api/notes", json={"title": "T", "category": "c", "content": "body"})
    mock_turso.assert_called()
    call_sql = mock_turso.call_args_list[0][0][0]
    assert "INSERT INTO notes" in call_sql


async def test_create_note_stores_embedding_in_chromadb(client, mock_turso, mock_vector_store, mock_embedding):
    await client.post("/api/notes", json={"title": "T", "category": "c", "content": "body"})
    mock_embedding["embed"].assert_called_once_with("body")
    mock_vector_store["upsert"].assert_called_once()


async def test_get_all_notes_returns_list(client, mock_turso):
    mock_turso.return_value = make_turso_result([NOTE_ROW])
    resp = await client.get("/api/notes")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["title"] == "Why Alicante"


async def test_get_note_by_id_returns_note(client, mock_turso):
    mock_turso.return_value = make_turso_result([NOTE_ROW])
    resp = await client.get("/api/notes/note-id-1")
    assert resp.status_code == 200
    assert resp.json()["id"] == "note-id-1"


async def test_get_note_not_found_returns_404(client, mock_turso):
    mock_turso.return_value = make_turso_result([])
    resp = await client.get("/api/notes/does-not-exist")
    assert resp.status_code == 404


async def test_delete_note_removes_from_turso(client, mock_turso):
    mock_turso.side_effect = [
        make_turso_result([make_turso_row("note-id-1")]),  # SELECT check
        make_turso_result([]),  # DELETE
    ]
    resp = await client.delete("/api/notes/note-id-1")
    assert resp.status_code == 204
    delete_call = mock_turso.call_args_list[1][0][0]
    assert "DELETE FROM notes" in delete_call


async def test_delete_note_removes_from_chromadb(client, mock_turso, mock_vector_store):
    mock_turso.side_effect = [
        make_turso_result([make_turso_row("note-id-1")]),
        make_turso_result([]),
    ]
    await client.delete("/api/notes/note-id-1")
    mock_vector_store["delete"].assert_called_once_with("note-id-1")


async def test_note_missing_title_returns_422(client):
    resp = await client.post("/api/notes", json={"category": "c", "content": "body"})
    assert resp.status_code == 422
