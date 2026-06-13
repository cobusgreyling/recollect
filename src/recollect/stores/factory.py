from __future__ import annotations

from pathlib import Path

from recollect.config import RecollectConfig
from recollect.stores.base import MemoryStore
from recollect.stores.in_memory_store import InMemoryStore
from recollect.stores.sqlite_store import SQLiteMemoryStore


def create_store(config: RecollectConfig) -> MemoryStore:
    vs = config.vector_store
    if vs.provider in ("memory", "inmemory"):
        return InMemoryStore()
    if vs.provider == "sqlite":
        db_path = vs.sqlite_path or (config.data_dir / "memories.db")
        return SQLiteMemoryStore(Path(db_path))
    if vs.provider == "qdrant":
        from recollect.stores.qdrant_store import QdrantMemoryStore

        return QdrantMemoryStore(vs)
    if vs.provider == "chroma":
        from recollect.stores.chroma_store import ChromaMemoryStore

        if vs.chroma_path is None:
            vs = vs.model_copy(update={"chroma_path": str(config.data_dir / "chroma")})
        return ChromaMemoryStore(vs)
    if vs.provider == "pgvector":
        from recollect.stores.pgvector_store import PgVectorMemoryStore

        return PgVectorMemoryStore(vs)
    raise ValueError(f"Unknown vector store provider: {vs.provider}")
