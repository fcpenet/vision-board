from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.db import turso

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# In-memory cache — avoids a DB round-trip on every request
_cached_key: str | None = None


async def _get_key() -> str:
    global _cached_key
    if _cached_key is None:
        result = await turso.execute("SELECT key FROM api_keys LIMIT 1")
        _cached_key = result.rows[0][0] if result.rows else ""
    return _cached_key


async def verify_api_key(api_key: str | None = Security(_api_key_header)) -> None:
    expected = await _get_key()
    if not expected:
        return  # no key in DB yet — skip (shouldn't happen after startup)
    if api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
