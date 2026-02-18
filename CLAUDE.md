# CLAUDE.md — Project Spain Vision Board

This file guides Claude Code's behavior throughout the `project-spain` monorepo. Read this before touching any file.

## Project Overview

A RAG-powered vision board and knowledge base for Kiko's Spain Digital Nomad Visa journey. The app stores decisions, notes, and documents, and exposes a "mini me" chat interface that answers questions by retrieving relevant context via RAG.

**Example queries the chat should answer:**
- "Why did we choose Alicante over Granada?"
- "What documents do I still need for the DNV?"
- "What's the income requirement for adding a dependent?"

## Monorepo Structure

```
project-spain/
├── frontend/       # React + Vite + TailwindCSS
├── backend/        # Python FastAPI
├── shared/         # Shared constants (checklist categories, status enums)
├── CLAUDE.md       # This file
└── README.md
```

## Tech Stack

### Backend

| Concern | Tool |
|---|---|
| Framework | FastAPI |
| Structured data | Turso (libSQL) via `libsql-client` |
| Vector store | ChromaDB |
| RAG orchestration | LangChain |
| Embeddings + Chat | OpenAI (`text-embedding-3-small` + `gpt-4o`) |
| PDF parsing | PyMuPDF (`fitz`) |
| Testing | pytest + pytest-asyncio |
| Env management | python-dotenv |

### Frontend

| Concern | Tool |
|---|---|
| Framework | React + Vite |
| Styling | TailwindCSS |
| Data fetching | React Query (TanStack Query) |
| Routing | React Router v6 |
| HTTP client | Axios |
| Testing | Vitest + React Testing Library |

### Hosting
- **Frontend** → Vercel
- **Backend** → Railway
- **Database** → Turso (cloud, already provisioned)
- **Vector store** → ChromaDB (persisted locally on Railway volume)

## Environment Variables

### Backend `.env`

```
OPENAI_API_KEY=
TURSO_DATABASE_URL=libsql://your-db.turso.io
TURSO_AUTH_TOKEN=
CHROMA_PERSIST_DIR=./chroma_db
ALLOWED_ORIGINS=http://localhost:5173,https://your-vercel-app.vercel.app
```

### Frontend `.env`

```
VITE_API_BASE_URL=http://localhost:8000
```

## Data Architecture

### Turso (structured data)

Stores metadata and relational data only — never raw content.

```sql
-- notes: metadata only, content lives in ChromaDB
CREATE TABLE notes (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  category TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

-- checklist items
CREATE TABLE checklist_items (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT,
  category TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending', -- pending | in_progress | done
  due_date TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

-- uploaded documents metadata
CREATE TABLE documents (
  id TEXT PRIMARY KEY,
  filename TEXT NOT NULL,
  file_type TEXT NOT NULL,
  uploaded_at TEXT NOT NULL,
  chunk_count INTEGER
);

-- chat history (optional)
CREATE TABLE chat_history (
  id TEXT PRIMARY KEY,
  role TEXT NOT NULL,    -- user | assistant
  content TEXT NOT NULL,
  sources TEXT,          -- JSON array of source note IDs
  created_at TEXT NOT NULL
);
```

### ChromaDB (vector data)

Stores chunked content + embeddings for RAG retrieval.

```
Collection: "project_spain"
  - Each document = one chunk
  - Metadata: { source_id, source_type (note|document), title, category }
```

## Backend Directory Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app init, CORS, router registration
│   ├── config.py            # Settings via pydantic-settings
│   ├── api/
│   │   └── routes/
│   │       ├── notes.py     # CRUD for notes
│   │       ├── chat.py      # RAG chat endpoint
│   │       ├── checklist.py # CRUD for checklist items
│   │       └── documents.py # PDF upload + parsing
│   ├── services/
│   │   ├── rag_service.py       # LangChain retrieval + prompt assembly
│   │   ├── embedding_service.py # OpenAI embeddings wrapper
│   │   └── chat_service.py      # OpenAI chat completion wrapper
│   ├── models/
│   │   ├── note.py
│   │   ├── checklist.py
│   │   └── document.py
│   ├── db/
│   │   ├── turso.py         # Turso client init + query helpers
│   │   └── vector_store.py  # ChromaDB init + upsert/query helpers
│   └── tests/
│       ├── conftest.py      # Shared fixtures (test client, mock DB)
│       ├── test_notes.py
│       ├── test_chat.py
│       ├── test_checklist.py
│       └── test_documents.py
├── seed/
│   └── seed.py              # Pre-load Alicante decision, DNV checklist
├── requirements.txt
├── .env.example
└── Procfile                 # For Railway: web: uvicorn app.main:app --host 0.0.0.0
```

## Frontend Directory Structure

```
frontend/
├── src/
│   ├── pages/
│   │   ├── VisionBoard.jsx  # Pin goals, images, milestones
│   │   ├── Chat.jsx         # RAG chat UI
│   │   ├── Checklist.jsx    # DNV requirements tracker
│   │   └── Notes.jsx        # Knowledge base notes
│   ├── components/
│   │   ├── NoteCard.jsx
│   │   ├── ChecklistItem.jsx
│   │   ├── ChatWindow.jsx
│   │   ├── ChatMessage.jsx
│   │   └── DocumentUpload.jsx
│   ├── hooks/
│   │   ├── useNotes.js
│   │   ├── useChecklist.js
│   │   └── useChat.js
│   ├── api/
│   │   └── client.js        # Axios instance with base URL
│   └── tests/
│       ├── VisionBoard.test.jsx
│       ├── Checklist.test.jsx
│       ├── Chat.test.jsx
│       └── Notes.test.jsx
├── index.html
├── vite.config.js
├── tailwind.config.js
└── package.json
```

## TDD Rules — Follow Strictly

**Always write tests before implementation.** The workflow for every feature is:

1. Write failing tests
2. Run tests — confirm they fail
3. Implement the minimum code to pass
4. Run tests — confirm they pass
5. Refactor if needed

### Backend Tests (pytest)

**Notes**
```
test_create_note_returns_201
test_create_note_stores_metadata_in_turso
test_create_note_stores_embedding_in_chromadb
test_get_all_notes_returns_list
test_get_note_by_id_returns_note
test_get_note_not_found_returns_404
test_delete_note_removes_from_turso
test_delete_note_removes_from_chromadb
test_note_missing_title_returns_422
```

**Chat (RAG)**
```
test_chat_returns_200_with_response
test_chat_retrieves_relevant_context_from_chromadb
test_chat_injects_context_into_prompt
test_chat_returns_source_references
test_chat_with_no_relevant_context_still_responds
test_chat_empty_query_returns_400
test_chat_response_contains_answer_field
test_chat_response_contains_sources_field
```

**Checklist**
```
test_create_checklist_item_returns_201
test_create_checklist_item_persists_to_turso
test_get_checklist_items_returns_list
test_get_checklist_by_category
test_update_checklist_status_to_done
test_update_checklist_status_to_in_progress
test_invalid_status_returns_422
test_delete_checklist_item_removes_from_turso
```

**Documents**
```
test_upload_pdf_returns_200
test_upload_pdf_stores_metadata_in_turso
test_upload_pdf_chunks_and_stores_embeddings_in_chromadb
test_upload_non_pdf_returns_400
test_uploaded_doc_is_queryable_via_chat
test_chunk_count_stored_in_turso
```

**Turso**
```
test_turso_connection_succeeds
test_turso_insert_and_fetch
test_turso_update
test_turso_delete
```

### Frontend Tests (Vitest + RTL)

```
test_renders_vision_board_page
test_renders_checklist_with_items
test_checklist_item_toggle_calls_api
test_checklist_filters_by_category
test_chat_input_submits_query
test_chat_displays_assistant_response
test_chat_displays_source_references
test_note_form_submit_adds_note_to_list
test_document_upload_shows_success_state
test_document_upload_shows_error_on_non_pdf
```

## RAG Pipeline

```
User query
  ↓
Embed query (OpenAI text-embedding-3-small)
  ↓
ChromaDB similarity search → top 5 chunks
  ↓
Assemble system prompt with retrieved context
  ↓
OpenAI gpt-4o generates answer
  ↓
Return { answer, sources[] }
```

### System Prompt Template

```
You are a personal assistant helping Kiko track his Spain Digital Nomad Visa
journey. You have access to his notes, decisions, and uploaded documents.

Answer questions based ONLY on the context provided below. If the answer
is not in the context, say "I don't have that information yet — consider
adding a note about it."

Always cite which note or document you're referencing.

Context:
{retrieved_chunks}
```

## Seed Data

Run `python seed/seed.py` on first setup. This pre-loads:

### Notes

```json
[
  {
    "title": "Why Alicante over Granada",
    "category": "decisions",
    "content": "Chose Alicante for its 320+ sunny days, strong nightlife, and coastal tourism infrastructure."
  },
  {
    "title": "Visa Strategy",
    "category": "visa",
    "content": "Applying via UGE (Unidad de Grandes Empresas) for fast-track processing (~20 days)."
  },
  {
    "title": "About Alicante",
    "category": "city",
    "content": "Alicante is on Spain's Costa Blanca (southeastern coast). 320+ sunny days per year."
  }
]
```

### Checklist (DNV Requirements)

```json
[
  { "title": "Valid passport (1yr+ validity)", "category": "documents", "status": "pending" },
  { "title": "Completed national visa application form", "category": "documents", "status": "pending" },
  { "title": "Passport photos", "category": "documents", "status": "pending" },
  { "title": "Criminal background check (apostilled)", "category": "documents", "status": "pending" },
  { "title": "Health insurance (100% coverage, no co-pay)", "category": "insurance", "status": "pending" },
  { "title": "Proof of income (€2,368+/month)", "category": "financial", "status": "pending" },
  { "title": "Employment contract or client contracts", "category": "financial", "status": "pending" },
  { "title": "Bank statements (3 months)", "category": "financial", "status": "pending" },
  { "title": "Visa fee payment (~₱10,000 via BLS)", "category": "financial", "status": "pending" },
  { "title": "Partner: passport", "category": "dependent", "status": "pending" },
  { "title": "Partner: family visa application form", "category": "dependent", "status": "pending" },
  { "title": "Partner: proof of relationship (marriage/partnership cert)", "category": "dependent", "status": "pending" },
  { "title": "Partner: criminal background check (apostilled)", "category": "dependent", "status": "pending" },
  { "title": "Partner: health insurance", "category": "dependent", "status": "pending" },
  { "title": "Choose visa agency (LAKBYTE vs BLS)", "category": "admin", "status": "pending" },
  { "title": "Book BLS/consulate appointment", "category": "admin", "status": "pending" }
]
```

## API Endpoints

```
POST   /api/notes                Create note (stores in Turso + ChromaDB)
GET    /api/notes                List all notes
GET    /api/notes/{id}           Get note by ID
DELETE /api/notes/{id}           Delete note (removes from Turso + ChromaDB)

POST   /api/chat                 RAG chat query → { answer, sources }

GET    /api/checklist            List all checklist items
GET    /api/checklist?category=documents  Filter by category
POST   /api/checklist            Create checklist item
PATCH  /api/checklist/{id}       Update status
DELETE /api/checklist/{id}       Delete item

POST   /api/documents/upload     Upload PDF → parse, chunk, embed
GET    /api/documents            List uploaded documents
DELETE /api/documents/{id}       Delete document + embeddings
```

## Code Style

- **Backend:** Follow PEP8, use type hints everywhere, async/await for all DB calls
- **Frontend:** Functional components only, no class components
- **No hardcoded secrets** — always use env vars
- **Error handling:** All API routes must return consistent error shape: `{ "error": "message" }`
- **IDs:** Use `uuid4()` for all record IDs

## Claude Code Bootstrap Command

Feed this to Claude Code to start the project:

```
Read CLAUDE.md fully before writing any code.

Scaffold the full monorepo structure for project-spain as defined in CLAUDE.md.
Then follow TDD strictly:
1. Write all backend pytest tests first (they should fail)
2. Implement backend to make tests pass
3. Write all frontend Vitest tests (they should fail)
4. Implement frontend to make tests pass

Start with: monorepo scaffold → backend tests → backend implementation → seed script → frontend tests → frontend implementation
```
