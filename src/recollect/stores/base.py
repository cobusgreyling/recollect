from __future__ import annotations

from typing import Iterable, Protocol

import numpy as np

from recollect.types import MemoryRecord


class MemoryStore(Protocol):
    def insert(self, record: MemoryRecord, embedding: np.ndarray) -> None: ...

    def delete(self, memory_id: str) -> bool: ...

    def get(self, memory_id: str) -> MemoryRecord | None: ...

    def list_all(self, filters: dict[str, str] | None = None) -> list[MemoryRecord]: ...

    def iter_with_embeddings(
        self, filters: dict[str, str] | None = None
    ) -> Iterable[tuple[MemoryRecord, np.ndarray]]: ...

    def close(self) -> None: ...