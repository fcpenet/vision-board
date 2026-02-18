import pytest
from .conftest import make_turso_result

pytestmark = pytest.mark.asyncio

CONTEXT_RESULT = {
    "documents": [["Alicante has 320 sunny days."]],
    "metadatas": [[{"source_id": "note-1", "source_type": "note", "title": "Why Alicante", "category": "decisions"}]],
    "distances": [[0.1]],
}


async def test_chat_returns_200_with_response(client):
    resp = await client.post("/api/chat", json={"query": "Why Alicante?"})
    assert resp.status_code == 200


async def test_chat_retrieves_relevant_context_from_chromadb(client, mock_vector_store, mock_embedding):
    mock_vector_store["query"].return_value = CONTEXT_RESULT
    await client.post("/api/chat", json={"query": "Why Alicante?"})
    mock_embedding["embed"].assert_called_once_with("Why Alicante?")
    mock_vector_store["query"].assert_called_once()


async def test_chat_injects_context_into_prompt(client, mock_vector_store, mock_chat_complete):
    mock_vector_store["query"].return_value = CONTEXT_RESULT
    await client.post("/api/chat", json={"query": "Why Alicante?"})
    call_args = mock_chat_complete.call_args
    system_prompt = call_args[0][0]
    assert "Alicante has 320 sunny days" in system_prompt


async def test_chat_returns_source_references(client, mock_vector_store):
    mock_vector_store["query"].return_value = CONTEXT_RESULT
    resp = await client.post("/api/chat", json={"query": "Why Alicante?"})
    data = resp.json()
    assert "note-1" in data["sources"]


async def test_chat_with_no_relevant_context_still_responds(client, mock_vector_store, mock_chat_complete):
    mock_vector_store["query"].return_value = {"documents": [[]], "metadatas": [[]], "distances": [[]]}
    mock_chat_complete.return_value = "I don't have that information yet."
    resp = await client.post("/api/chat", json={"query": "random question"})
    assert resp.status_code == 200
    assert resp.json()["answer"] != ""


async def test_chat_empty_query_returns_400(client):
    resp = await client.post("/api/chat", json={"query": "   "})
    assert resp.status_code == 400


async def test_chat_response_contains_answer_field(client):
    resp = await client.post("/api/chat", json={"query": "test"})
    assert "answer" in resp.json()


async def test_chat_response_contains_sources_field(client):
    resp = await client.post("/api/chat", json={"query": "test"})
    assert "sources" in resp.json()
