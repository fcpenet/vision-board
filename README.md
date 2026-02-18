# Project Spain — Vision Board

RAG-powered vision board and knowledge base for Kiko's Spain Digital Nomad Visa journey.

## Quick Start

### Backend
```bash
cd backend
cp .env.example .env   # fill in your keys
pip install -r requirements.txt
python seed/seed.py    # load initial data
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
cp .env.example .env   # set VITE_API_BASE_URL
npm install
npm run dev
```

### Tests
```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm test
```

## Stack
- **Backend**: FastAPI + Turso (libSQL) + ChromaDB + LangChain + OpenAI
- **Frontend**: React + Vite + TailwindCSS + React Query
- **Hosting**: Vercel (frontend) · Railway (backend) · Turso cloud (DB)

---

## How the Backend Works

### Data Layer — two stores working together

**Turso (libSQL)** stores only *metadata* — note titles, checklist statuses, document filenames, timestamps. It never holds raw content.

**ChromaDB** stores the actual *content as vector embeddings*. Every piece of text (note bodies, PDF chunks) is embedded via OpenAI's `text-embedding-3-small` and saved here with metadata linking it back to its Turso record (`source_id`).

This split means structured queries (filter checklist by category) hit Turso, while semantic search hits ChromaDB.

### Four API surfaces

| Route | What it does |
|---|---|
| `/api/notes` | CRUD — on create, embeds content → ChromaDB; on delete, removes from both stores |
| `/api/checklist` | CRUD for DNV requirement items; status lifecycle: `pending → in_progress → done` |
| `/api/documents` | Accepts PDF upload, extracts text via PyMuPDF, chunks it (~500 words, 50 overlap), embeds all chunks → ChromaDB |
| `/api/chat` | RAG pipeline — see below |

### RAG Pipeline (`POST /api/chat`)

```
1. Embed the user's query (text-embedding-3-small)
2. ChromaDB similarity search → top 5 chunks
3. Assemble system prompt with retrieved chunks injected
4. gpt-4o generates an answer, citing sources
5. Return { answer, sources[] }
```

The system prompt instructs the model to answer *only from retrieved context*, and to say "I don't have that information yet" if nothing relevant was found.

### Startup

On boot, `lifespan` runs `init_db()` which issues `CREATE TABLE IF NOT EXISTS` for all four tables (`notes`, `checklist_items`, `documents`, `chat_history`). First-time setup also requires running `seed/seed.py` to pre-load the Alicante decision notes and the 16-item DNV checklist.

---

## How the Frontend Works

The frontend is a **React + Vite** SPA with four pages, using React Query for server state and Axios for HTTP.

### Routing

React Router v6 handles four routes:

| Path | Page | Purpose |
|---|---|---|
| `/` | `VisionBoard` | Home — milestones overview + nav to other pages |
| `/checklist` | `Checklist` | DNV requirements tracker |
| `/chat` | `Chat` | RAG "mini-me" chat interface |
| `/notes` | `Notes` | Knowledge base — add/view/delete notes |

### Data fetching — React Query + Axios

`src/api/client.js` is a single Axios instance pointed at `VITE_API_BASE_URL`. All API calls go through it.

Three custom hooks wrap React Query:
- **`useNotes`** — fetches/creates/deletes notes
- **`useChecklist`** — fetches items (optionally filtered by category), updates status
- **`useChat`** — local state only (no caching needed); sends query to `/api/chat`, appends messages to a list

### Pages & Components

**VisionBoard** — static milestone cards + nav links, no API calls.

**Checklist** — fetches items from `/api/checklist`, renders `ChecklistItem` components. Category filter buttons re-fetch with `?category=` param. Clicking a checkbox calls `PATCH /api/checklist/{id}` to toggle `pending ↔ done`.

**Chat** — maintains a local `messages[]` array. On form submit it calls `POST /api/chat`, then appends both the user message and the assistant's `{ answer, sources }` response to the list. `ChatWindow` scrolls to bottom on each new message.

**Notes** — fetches notes list, renders `NoteCard` grid. A form at the top posts title + content + category to `POST /api/notes`. `DocumentUpload` component lets users upload PDFs — validates `.pdf` extension client-side before posting as `multipart/form-data` to `/api/documents/upload`.

### State Management Philosophy

No global state store — React Query owns all server state (caches, refetches on mutation). The only local state is the chat message history and form inputs.
