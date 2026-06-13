from __future__ import annotations

import logging
from typing import Any

from recollect.config import RecollectConfig
from recollect.embeddings import Embedder
from recollect.extraction import FactExtractor, extract_entities_heuristic, parse_messages
from recollect.retrieval import hybrid_search
from recollect.stores.base import MemoryStore
from recollect.stores.factory import create_store
from recollect.types import MemoryRecord, MemoryScope, SearchHit

logger = logging.getLogger(__name__)


class MemoryCore:
    def __init__(
        self, config: RecollectConfig | None = None, store: MemoryStore | None = None
    ) -> None:
        self.config = config or RecollectConfig()
        self._store = store or create_store(self.config)
        self._embedder = Embedder(self.config.embedder)
        self._extractor: FactExtractor | None = None
        if self.config.extraction_enabled and self.config.llm.api_key:
            self._extractor = FactExtractor(self.config.llm)

    def _scope_kwargs(
        self,
        *,
        user_id: str | None,
        agent_id: str | None,
        run_id: str | None,
        metadata: dict[str, Any] | None,
    ) -> MemoryScope:
        return MemoryScope(
            user_id=user_id,
            agent_id=agent_id,
            run_id=run_id,
            metadata=metadata or {},
        )

    def _filters_from_scope(self, scope: MemoryScope) -> dict[str, str]:
        return scope.as_filters()

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
        scope = self._scope_kwargs(
            user_id=user_id, agent_id=agent_id, run_id=run_id, metadata=metadata
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
        logger.debug("Added %d fact(s) (infer=%s, scoped)", len(created), infer)
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
        logger.debug(
            "Search returned %d hit(s) from %d candidates (top_k=%d)", len(hits), len(candidates), k
        )
        return {"results": [hit.model_dump() for hit in hits]}

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
