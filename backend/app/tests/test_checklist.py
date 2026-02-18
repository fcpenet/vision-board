import pytest
from .conftest import make_turso_result, make_turso_row

pytestmark = pytest.mark.asyncio

ITEM_ROW = make_turso_row(
    "item-id-1", "Valid passport", None, "documents",
    "pending", None,
    "2024-01-01T00:00:00+00:00", "2024-01-01T00:00:00+00:00",
)


async def test_create_checklist_item_returns_201(client):
    resp = await client.post("/api/checklist", json={"title": "Valid passport", "category": "documents"})
    assert resp.status_code == 201


async def test_create_checklist_item_persists_to_turso(client, mock_turso):
    await client.post("/api/checklist", json={"title": "Valid passport", "category": "documents"})
    call_sql = mock_turso.call_args_list[0][0][0]
    assert "INSERT INTO checklist_items" in call_sql


async def test_get_checklist_items_returns_list(client, mock_turso):
    mock_turso.return_value = make_turso_result([ITEM_ROW])
    resp = await client.get("/api/checklist")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["title"] == "Valid passport"


async def test_get_checklist_by_category(client, mock_turso):
    mock_turso.return_value = make_turso_result([ITEM_ROW])
    resp = await client.get("/api/checklist?category=documents")
    assert resp.status_code == 200
    call_sql = mock_turso.call_args_list[0][0][0]
    assert "category" in call_sql.lower()


async def test_update_checklist_status_to_done(client, mock_turso):
    mock_turso.side_effect = [
        make_turso_result([ITEM_ROW]),  # SELECT
        make_turso_result([]),          # UPDATE
    ]
    resp = await client.patch("/api/checklist/item-id-1", json={"status": "done"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "done"


async def test_update_checklist_status_to_in_progress(client, mock_turso):
    mock_turso.side_effect = [
        make_turso_result([ITEM_ROW]),
        make_turso_result([]),
    ]
    resp = await client.patch("/api/checklist/item-id-1", json={"status": "in_progress"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_progress"


async def test_invalid_status_returns_422(client):
    resp = await client.patch("/api/checklist/item-id-1", json={"status": "invalid_status"})
    assert resp.status_code == 422


async def test_delete_checklist_item_removes_from_turso(client, mock_turso):
    mock_turso.side_effect = [
        make_turso_result([make_turso_row("item-id-1")]),
        make_turso_result([]),
    ]
    resp = await client.delete("/api/checklist/item-id-1")
    assert resp.status_code == 204
    delete_call = mock_turso.call_args_list[1][0][0]
    assert "DELETE FROM checklist_items" in delete_call
