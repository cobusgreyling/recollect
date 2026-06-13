from __future__ import annotations

from typing import Any

from recollect.config import RecollectConfig
from recollect.embeddings import Embedder
from recollect.extraction import FactExtractor, extract_entities_heuristic, parse_messages
from recollect.retrieval import hybrid_search
from recollect.stores.sqlite_store import SQLiteMemoryStore
from recollect.types import MemoryRecord, MemoryScope, SearchHit


class Memory:
    """High-level memory API: extract facts, store, and retrieve with hybrid ranking."""

    def __init__(self, config: RecollectConfig | None = None) -> None:
        self.config = config or RecollectConfig()
        db_path = self.config.data_dir / "memories.db"
        self._store = SQLiteMemoryStore(db_path)
        self._embedder = Embedder(self.config.embedder)
        self._extractor: FactExtractor | None = None
        if self.config.extraction_enabled and self.config.llm.api_key:
            self._extractor = FactExtractor(self.config.llm)

    def add(
        self,
        messages: str | list[dict[str, Any]],
        *,
        user_id: str | None = None,
        agent_id: str | None = None,
        run_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        infer: bool = True,
    ) -> dict[str, Any]:
        scope = MemoryScope(
            user_id=user_id,
            agent_id=agent_id,
            run_id=run_id,
            metadata=metadata or {},
        )
        parsed = parse_messages(messages)
        facts: list[str] = []
        if infer and self._extractor:
            facts = self._extractor.extract(parsed)
        elif infer:
            facts = [m["content"] for m in parsed if m["role"] in ("user", "assistant")]
        else:
            facts = [m["content"] for m in parsed]

        created: list[dict[str, str]] = []
        for fact in facts:
            record = MemoryRecord(
                text=fact,
                scope=scope,
                entities=extract_entities_heuristic(fact),
            )
            embedding = self._embedder.embed(fact)
            self._store.insert(record, embedding)
            created.append({"id": record.id, "memory": record.text})

        return {"results": created}

    def search(
        self,
        query: str,
        *,
        filters: dict[str, str] | None = None,
        top_k: int | None = None,
    ) -> dict[str, Any]:
        k = top_k or self.config.default_top_k
        query_embedding = self._embedder.embed(query)
        candidates = list(self._store.iter_with_embeddings(filters))
        hits: list[SearchHit] = hybrid_search(
            query=query,
            query_embedding=query_embedding,
            candidates=candidates,
            config=self.config,
            top_k=k,
        )
        return {
            "results": [hit.model_dump() for hit in hits],
        }

    def get(self, memory_id: str) -> dict[str, Any] | None:
        record = self._store.get(memory_id)
        if not record:
            return None
        return {
            "id": record.id,
            "memory": record.text,
            "scope": record.scope.model_dump(),
            "entities": record.entities,
            "created_at": record.created_at.isoformat(),
        }

    def get_all(self, filters: dict[str, str] | None = None) -> dict[str, Any]:
        records = self._store.list_all(filters)
        return {
            "results": [
                {
                    "id": r.id,
                    "memory": r.text,
                    "scope": r.scope.model_dump(),
                    "entities": r.entities,
                    "created_at": r.created_at.isoformat(),
                }
                for r in records
            ]
        }

    def delete(self, memory_id: str) -> dict[str, str]:
        deleted = self._store.delete(memory_id)
        if not deleted:
            return {"message": "not_found"}
        return {"message": "deleted"}

    def close(self) -> None:
        self._store.close()