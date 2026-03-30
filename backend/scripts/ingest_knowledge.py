"""
backend/scripts/ingest_knowledge.py
批量将 knowledge.jsonl 种子数据导入 SQLite 数据库 + ChromaDB 向量库。

用法（在 backend/ 目录下执行）:
    python scripts/ingest_knowledge.py
    python scripts/ingest_knowledge.py --file data/knowledge.jsonl --batch-size 50

选项:
    --file          JSONL 文件路径（默认: <script_dir>/../data/knowledge.jsonl）
    --batch-size    每批入库条数（默认: 50）
    --skip-existing 遇到同标题文档时跳过（不重复入库）
    --dry-run       只解析文件，不写入数据库
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List

# ── Ensure backend package root is on sys.path ────────────────────────────────
_BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_BACKEND_DIR))

from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.core.database import Base  # noqa: E402
from app.models.knowledge import KnowledgeDocument  # noqa: F401 (registers model)
from app.models.user import User  # noqa: F401 (registers model — FK target)
from app.rag.vector_store import VectorStore  # noqa: E402
from app.schemas.knowledge import KnowledgeCreate  # noqa: E402
from app.services.knowledge import bulk_create_knowledge  # noqa: E402

# ── Tag → category mapping ────────────────────────────────────────────────────

_TAG_TO_CATEGORY = {
    "病害": "disease",
    "虫害": "pest",
    "栽培技术": "technique",
    "农业政策": "policy",
    "气象灾害": "weather",
}

_DEFAULT_JSONL = _BACKEND_DIR / "data" / "knowledge.jsonl"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _seed_to_create(record: dict) -> KnowledgeCreate:
    """Convert a knowledge seed dict to a KnowledgeCreate schema object."""
    tags: List[str] = record.get("tags", [])

    # Derive category from the second tag (first tag is crop name)
    category = "technique"  # sensible default
    for tag in tags:
        if tag in _TAG_TO_CATEGORY:
            category = _TAG_TO_CATEGORY[tag]
            break

    # The first tag is typically the crop name
    crop_tag = tags[0] if tags else None
    crop_types = crop_tag if crop_tag and crop_tag not in _TAG_TO_CATEGORY else None

    return KnowledgeCreate(
        title=record["title"],
        category=category,
        content=record["content"],
        crop_types=crop_types,
        is_verified=True,
    )


def _load_jsonl(path: Path) -> List[dict]:
    """Load and parse all records from a JSONL file."""
    records = []
    with open(path, encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, 1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                records.append(json.loads(raw))
            except json.JSONDecodeError as exc:
                print(f"  [WARN] line {lineno} JSON parse error: {exc}", file=sys.stderr)
    return records


# ── Main ingestion logic ──────────────────────────────────────────────────────

def ingest(
    jsonl_path: Path,
    batch_size: int = 50,
    skip_existing: bool = False,
    dry_run: bool = False,
    db_url: str | None = None,
    vector_store: VectorStore | None = None,
) -> int:
    """
    Ingest records from *jsonl_path* into SQLite + ChromaDB.

    Returns the total number of documents inserted.
    """
    print(f"[ingest] Loading {jsonl_path} …")
    records = _load_jsonl(jsonl_path)
    print(f"[ingest] Loaded {len(records)} records.")

    if dry_run:
        print("[ingest] --dry-run: skipping database writes.")
        for rec in records[:5]:
            kc = _seed_to_create(rec)
            print(f"  sample → title={kc.title!r}, category={kc.category!r}, crop_types={kc.crop_types!r}")
        return 0

    # Set up SQLAlchemy engine + session
    url = db_url or settings.DATABASE_URL
    engine = create_engine(url, connect_args={"check_same_thread": False} if "sqlite" in url else {})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Set up vector store
    vs = vector_store or VectorStore(
        persist_dir=settings.CHROMA_PERSIST_DIR,
        embedding_backend=settings.CHROMA_EMBEDDING_BACKEND,
    )

    total_inserted = 0

    with Session() as db:
        # Optionally skip titles that already exist
        existing_titles: set[str] = set()
        if skip_existing:
            existing_titles = {row[0] for row in db.query(KnowledgeDocument.title).all()}
            print(f"[ingest] Found {len(existing_titles)} existing titles — duplicates will be skipped.")

        batch: List[KnowledgeCreate] = []

        for idx, rec in enumerate(records):
            title = rec.get("title", "")
            if skip_existing and title in existing_titles:
                continue

            batch.append(_seed_to_create(rec))

            if len(batch) >= batch_size:
                count = bulk_create_knowledge(db, batch, vs=vs)
                total_inserted += count
                print(f"[ingest] Inserted batch ({count} docs, total so far: {total_inserted})")
                batch = []

        # Flush remaining
        if batch:
            count = bulk_create_knowledge(db, batch, vs=vs)
            total_inserted += count
            print(f"[ingest] Inserted final batch ({count} docs, total so far: {total_inserted})")

    print(f"[ingest] Done. Total inserted: {total_inserted}")
    return total_inserted


# ── CLI entry point ───────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="批量将 knowledge.jsonl 种子数据导入 SQLite + ChromaDB"
    )
    parser.add_argument(
        "--file",
        default=str(_DEFAULT_JSONL),
        help=f"JSONL 文件路径（默认: {_DEFAULT_JSONL}）",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        dest="batch_size",
        help="每批入库条数（默认: 50）",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        dest="skip_existing",
        help="遇到同标题文档时跳过，不重复入库",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        dest="dry_run",
        help="只解析文件，不写入数据库",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    ingest(
        jsonl_path=Path(args.file),
        batch_size=args.batch_size,
        skip_existing=args.skip_existing,
        dry_run=args.dry_run,
    )
