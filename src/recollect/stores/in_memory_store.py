from __future__ import annotations

from collections.abc import Iterable

import numpy as np

from recollect.stores.base import MemoryStore
from recollect.types import MemoryRecord


class InMemoryStore(MemoryStore):
    """Pure in-memory store. Ideal for unit tests, demos, and zero-persistence scenarios.

    Data is lost when the process exits. Filters are supported on user_id/agent_id/run_id.
    """

    def __init__(self) -> None:
        self._records: dict[str, MemoryRecord] = {}
        self._embeddings: dict[str, np.ndarray] = {}

    def insert(self, record: MemoryRecord, embedding: np.ndarray) -> None:
        self._records[record.id] = record
        self._embeddings[record.id] = np.asarray(embedding, dtype=np.float32)

    def delete(self, memory_id: str) -> bool:
        if memory_id in self._records:
            del self._records[memory_id]
            self._embeddings.pop(memory_id, None)
            return True
        return False

    def get(self, memory_id: str) -> MemoryRecord | None:
        return self._records.get(memory_id)

    def list_all(self, filters: dict[str, str] | None = None) -> list[MemoryRecord]:
        if not filters:
            return list(self._records.values())
        return [r for r in self._records.values() if r.matches_filters(filters)]

    def iter_with_embeddings(
        self, filters: dict[str, str] | None = None
    ) -> Iterable[tuple[MemoryRecord, np.ndarray]]:
        if not filters:
            for rid, rec in self._records.items():
                yield rec, self._embeddings[rid]
            return
        for rid, rec in self._records.items():
            if rec.matches_filters(filters):
                yield rec, self._embeddings[rid]

    def close(self) -> None:
        # Nothing to close; memory only
        pass
