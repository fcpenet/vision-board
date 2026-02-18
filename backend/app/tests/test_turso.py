import pytest
from unittest.mock import AsyncMock, MagicMock, patch

pytestmark = pytest.mark.asyncio


async def test_turso_connection_succeeds():
    mock_client = MagicMock()
    mock_client.execute = AsyncMock(return_value=MagicMock(rows=[]))
    with patch("app.db.turso.get_client", return_value=mock_client):
        from app.db.turso import execute
        result = await execute("SELECT 1")
        assert result is not None


async def test_turso_insert_and_fetch():
    inserted = []

    async def fake_execute(statement):
        sql = statement.sql if hasattr(statement, "sql") else str(statement)
        if "INSERT" in sql:
            inserted.append(statement)
            return MagicMock(rows=[])
        return MagicMock(rows=[("val",)])

    mock_client = MagicMock()
    mock_client.execute = fake_execute

    with patch("app.db.turso.get_client", return_value=mock_client):
        from app.db import turso as turso_module
        import libsql_client

        result = await turso_module.execute("INSERT INTO notes VALUES (?)", ["val"])
        assert result is not None


async def test_turso_update():
    mock_client = MagicMock()
    mock_client.execute = AsyncMock(return_value=MagicMock(rows=[]))
    with patch("app.db.turso.get_client", return_value=mock_client):
        from app.db.turso import execute
        result = await execute("UPDATE notes SET title = ? WHERE id = ?", ["new_title", "id-1"])
        assert result is not None


async def test_turso_delete():
    mock_client = MagicMock()
    mock_client.execute = AsyncMock(return_value=MagicMock(rows=[]))
    with patch("app.db.turso.get_client", return_value=mock_client):
        from app.db.turso import execute
        result = await execute("DELETE FROM notes WHERE id = ?", ["id-1"])
        assert result is not None
