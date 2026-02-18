import secrets
from datetime import datetime, timezone
import libsql_client
from app.config import settings

_client: libsql_client.Client | None = None


def get_client() -> libsql_client.Client:
    global _client
    if _client is None:
        _client = libsql_client.create_client(
            url=settings.turso_database_url,
            auth_token=settings.turso_auth_token,
        )
    return _client


async def execute(sql: str, args: list | None = None) -> libsql_client.ResultSet:
    client = get_client()
    return await client.execute(libsql_client.Statement(sql, args or []))


async def init_db() -> None:
    await execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            category TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    await execute("""
        CREATE TABLE IF NOT EXISTS checklist_items (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            due_date TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    await execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            file_type TEXT NOT NULL,
            uploaded_at TEXT NOT NULL,
            chunk_count INTEGER
        )
    """)
    await execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id TEXT PRIMARY KEY,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            sources TEXT,
            created_at TEXT NOT NULL
        )
    """)
    await execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY,
            key TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)


async def get_or_create_api_key() -> tuple[str, bool]:
    """Return (key, was_just_created). Generates and stores a key on first call."""
    result = await execute("SELECT key FROM api_keys LIMIT 1")
    if result.rows:
        return result.rows[0][0], False
    key = secrets.token_hex(32)
    now = datetime.now(timezone.utc).isoformat()
    await execute("INSERT INTO api_keys (key, created_at) VALUES (?, ?)", [key, now])
    return key, True
