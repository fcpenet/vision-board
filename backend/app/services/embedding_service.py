from openai import AsyncOpenAI
from app.config import settings

_client: AsyncOpenAI | None = None
EMBEDDING_MODEL = "text-embedding-3-small"


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


async def embed(text: str) -> list[float]:
    client = get_client()
    response = await client.embeddings.create(
        input=text,
        model=EMBEDDING_MODEL,
    )
    return response.data[0].embedding


async def embed_many(texts: list[str]) -> list[list[float]]:
    client = get_client()
    response = await client.embeddings.create(
        input=texts,
        model=EMBEDDING_MODEL,
    )
    return [item.embedding for item in response.data]
