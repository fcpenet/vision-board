from app.services.embedding_service import embed
from app.services.chat_service import complete, SYSTEM_PROMPT_TEMPLATE
from app.db.vector_store import query_chunks


async def chat(query: str) -> dict:
    query_embedding = await embed(query)
    results = query_chunks(query_embedding, n_results=5)

    chunks = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    context_parts = []
    sources = []
    for chunk, meta in zip(chunks, metadatas):
        source_id = meta.get("source_id", "")
        title = meta.get("title", "")
        context_parts.append(f"[{title}]: {chunk}")
        if source_id and source_id not in sources:
            sources.append(source_id)

    retrieved_chunks = "\n\n".join(context_parts) if context_parts else "No relevant context found."
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(retrieved_chunks=retrieved_chunks)
    answer = await complete(system_prompt, query)

    return {"answer": answer, "sources": sources}
