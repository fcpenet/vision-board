"""
Seed script — pre-loads Alicante decision notes and the DNV checklist.
Run once after init: python seed/seed.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.db.turso import init_db, execute
from app.db.vector_store import upsert_chunks
from app.services.embedding_service import embed
import uuid
from datetime import datetime, timezone


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


NOTES = [
    {
        "title": "Why Alicante over Granada",
        "category": "decisions",
        "content": (
            "Chose Alicante for its 320+ sunny days, strong expat community, "
            "coastal lifestyle, lower cost of living vs Barcelona/Madrid, "
            "and direct flights from Manila via Dubai or Doha. "
            "Granada was a runner-up but its inland location and fewer direct routes tipped the balance."
        ),
    },
    {
        "title": "Visa Strategy",
        "category": "visa",
        "content": (
            "Applying via UGE (Unidad de Grandes Empresas) for fast-track processing (~20 days). "
            "UGE handles Digital Nomad Visas for applicants with qualifying remote income. "
            "Alternative is the standard consulate route which takes 2-3 months."
        ),
    },
    {
        "title": "About Alicante",
        "category": "city",
        "content": (
            "Alicante is on Spain's Costa Blanca (southeastern coast). "
            "320+ sunny days per year. Population ~330,000. "
            "Strong expat and digital nomad scene. Affordable compared to Madrid/Barcelona. "
            "Has an international airport (ALC) with connections to major hubs."
        ),
    },
]

CHECKLIST = [
    {"title": "Valid passport (1yr+ validity)", "category": "documents"},
    {"title": "Completed national visa application form", "category": "documents"},
    {"title": "Passport photos", "category": "documents"},
    {"title": "Criminal background check (apostilled)", "category": "documents"},
    {"title": "Health insurance (100% coverage, no co-pay)", "category": "insurance"},
    {"title": "Proof of income (€2,368+/month)", "category": "financial"},
    {"title": "Employment contract or client contracts", "category": "financial"},
    {"title": "Bank statements (3 months)", "category": "financial"},
    {"title": "Visa fee payment (~₱10,000 via BLS)", "category": "financial"},
    {"title": "Partner: passport", "category": "dependent"},
    {"title": "Partner: family visa application form", "category": "dependent"},
    {"title": "Partner: proof of relationship (marriage/partnership cert)", "category": "dependent"},
    {"title": "Partner: criminal background check (apostilled)", "category": "dependent"},
    {"title": "Partner: health insurance", "category": "dependent"},
    {"title": "Choose visa agency (LAKBYTE vs BLS)", "category": "admin"},
    {"title": "Book BLS/consulate appointment", "category": "admin"},
]


async def seed_notes() -> None:
    print("Seeding notes...")
    for note in NOTES:
        note_id = str(uuid.uuid4())
        ts = now()
        await execute(
            "INSERT OR IGNORE INTO notes (id, title, category, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            [note_id, note["title"], note["category"], ts, ts],
        )
        embedding = await embed(note["content"])
        upsert_chunks(
            ids=[f"{note_id}_0"],
            documents=[note["content"]],
            embeddings=[embedding],
            metadatas=[{"source_id": note_id, "source_type": "note", "title": note["title"], "category": note["category"]}],
        )
        print(f"  + Note: {note['title']}")


async def seed_checklist() -> None:
    print("Seeding DNV checklist...")
    for item in CHECKLIST:
        item_id = str(uuid.uuid4())
        ts = now()
        await execute(
            "INSERT OR IGNORE INTO checklist_items (id, title, category, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            [item_id, item["title"], item["category"], "pending", ts, ts],
        )
        print(f"  + Checklist: {item['title']}")


async def main() -> None:
    print("Initialising database...")
    await init_db()
    await seed_notes()
    await seed_checklist()
    print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(main())
