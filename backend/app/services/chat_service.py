from openai import AsyncOpenAI
from app.config import settings

_client: AsyncOpenAI | None = None
CHAT_MODEL = "gpt-4o"

SYSTEM_PROMPT_TEMPLATE = """You are a personal assistant helping Kiko track his Spain Digital Nomad Visa journey. You have access to his notes, decisions, and uploaded documents.

Answer questions based ONLY on the context provided below. If the answer is not in the context, say "I don't have that information yet — consider adding a note about it."

Always cite which note or document you're referencing.

Context:
{retrieved_chunks}"""


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


async def complete(system_prompt: str, user_message: str) -> str:
    client = get_client()
    response = await client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content or ""
