from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime

import numpy as np

from recollect.config import VectorStoreConfig
from recollect.types import MemoryRecord, MemoryScope


class ChromaMemoryStore:
    def __init__(self, config: VectorStoreConfig) -> None:
        import chromadb

        if not config.chroma_path:
            raise ValueError("chroma_path must be set for chroma vector store")
        path = config.chroma_path
        self._client = chromadb.PersistentClient(path=path)
        self._collection = self._client.get_or_create_collection(config.collection_name)

    def insert(self, record: MemoryRecord, embedding: np.ndarray) -> None:
        scope = record.scope
        self._collection.upsert(
            ids=[record.id],
            embeddings=[embedding.tolist()],
            documents=[record.text],
            metadatas=[
                {
                    "user_id": scope.user_id or "",
                    "agent_id": scope.agent_id or "",
                    "run_id": scope.run_id or "",
                    "source": record.source,
                    "created_at": record.created_at.isoformat(),
                    "entities": ",".join(record.entities),
                }
            ],
        )

    def delete(self, memory_id: str) -> bool:
        try:
            # Pre-check existence for accurate return value
            existing = self._collection.get(ids=[memory_id], include=[])
            if not existing.get("ids"):
                return False
            self._collection.delete(ids=[memory_id])
            return True
        except Exception:
            return False

    def get(self, memory_id: str) -> MemoryRecord | None:
        result = self._collection.get(ids=[memory_id], include=["documents", "metadatas"])
        if not result["ids"]:
            return None
        return self._row_to_record(memory_id, result["documents"][0], result["metadatas"][0])

    def list_all(self, filters: dict[str, str] | None = None) -> list[MemoryRecord]:
        where = self._where(filters)
        result = self._collection.get(where=where, include=["documents", "metadatas"])
        return [
            self._row_to_record(rid, doc, meta)
            for rid, doc, meta in zip(
                result["ids"], result["documents"], result["metadatas"], strict=True
            )
        ]

    def iter_with_embeddings(
        self, filters: dict[str, str] | None = None
    ) -> Iterable[tuple[MemoryRecord, np.ndarray]]:
        where = self._where(filters)
        result = self._collection.get(where=where, include=["documents", "metadatas", "embeddings"])
        for rid, doc, meta, emb in zip(
            result["ids"],
            result["documents"],
            result["metadatas"],
            result["embeddings"],
            strict=True,
        ):
            yield self._row_to_record(rid, doc, meta), np.array(emb, dtype=np.float32)

    def _where(self, filters: dict[str, str] | None) -> dict | None:
        if not filters:
            return None
        clauses = [{k: filters[k]} for k in ("user_id", "agent_id", "run_id") if k in filters]
        if not clauses:
            return None
        if len(clauses) == 1:
            return clauses[0]
        return {"$and": clauses}

    def _row_to_record(self, rid: str, doc: str, meta: dict) -> MemoryRecord:
        entities_raw = meta.get("entities") or ""
        entities = [e for e in str(entities_raw).split(",") if e]
        return MemoryRecord(
            id=rid,
            text=doc,
            scope=MemoryScope(
                user_id=meta.get("user_id") or None,
                agent_id=meta.get("agent_id") or None,
                run_id=meta.get("run_id") or None,
                metadata={},
            ),
            entities=entities,
            source=str(meta.get("source", "conversation")),
            created_at=datetime.fromisoformat(str(meta.get("created_at"))),
        )

    def close(self) -> None:
        return None
