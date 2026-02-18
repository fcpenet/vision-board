from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db.turso import init_db, get_or_create_api_key
from app.api.routes import notes, chat, checklist, documents
from app.api.deps import verify_api_key


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    key, created = await get_or_create_api_key()
    if created:
        print("\n" + "=" * 60)
        print("  API key generated — save this, it won't be shown again:")
        print(f"  {key}")
        print("=" * 60 + "\n")
    yield


app = FastAPI(title="Project Spain API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(notes.router, dependencies=[Depends(verify_api_key)])
app.include_router(chat.router, dependencies=[Depends(verify_api_key)])
app.include_router(checklist.router, dependencies=[Depends(verify_api_key)])
app.include_router(documents.router, dependencies=[Depends(verify_api_key)])


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
