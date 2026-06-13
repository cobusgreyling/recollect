from __future__ import annotations

from datetime import datetime
from typing import Iterable

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, FieldCondition, Filter, MatchValue, PointStruct, VectorParams

from recollect.config import VectorStoreConfig
from recollect.types import MemoryRecord, MemoryScope


class QdrantMemoryStore:
    def __init__(self, config: VectorStoreConfig) -> None:
        self._dims = config.embedding_dims
        self._client = QdrantClient(host=config.qdrant_host, port=config.qdrant_port)
        self._collection = config.collection_name
        if not self._client.collection_exists(self._collection):
            self._client.create_collection(
                collection_name=self._collection,
                vectors_config=VectorParams(size=self._dims, distance=Distance.COSINE),
            )

    def insert(self, record: MemoryRecord, embedding: np.ndarray) -> None:
        scope = record.scope
        payload = {
            "text": record.text,
            "user_id": scope.user_id,
            "agent_id": scope.agent_id,
            "run_id": scope.run_id,
            "entities": record.entities,
            "metadata": scope.metadata,
            "source": record.source,
            "created_at": record.created_at.isoformat(),
        }
        self._client.upsert(
            collection_name=self._collection,
            points=[
                PointStruct(id=record.id, vector=embedding.tolist(), payload=payload),
            ],
        )

    def delete(self, memory_id: str) -> bool:
        self._client.delete(
            collection_name=self._collection,
            points_selector=[memory_id],
        )
        return True

    def get(self, memory_id: str) -> MemoryRecord | None:
        points = self._client.retrieve(collection_name=self._collection, ids=[memory_id])
        if not points:
            return None
        return self._point_to_record(memory_id, points[0].payload or {})

    def list_all(self, filters: dict[str, str] | None = None) -> list[MemoryRecord]:
        qfilter = self._build_filter(filters)
        records: list[MemoryRecord] = []
        offset = None
        while True:
            batch, offset = self._client.scroll(
                collection_name=self._collection,
                scroll_filter=qfilter,
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=False,
            )
            for point in batch:
                records.append(self._point_to_record(str(point.id), point.payload or {}))
            if offset is None:
                break
        return records

    def iter_with_embeddings(
        self, filters: dict[str, str] | None = None
    ) -> Iterable[tuple[MemoryRecord, np.ndarray]]:
        qfilter = self._build_filter(filters)
        offset = None
        while True:
            batch, offset = self._client.scroll(
                collection_name=self._collection,
                scroll_filter=qfilter,
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=True,
            )
            for point in batch:
                vec = np.array(point.vector, dtype=np.float32)
                yield self._point_to_record(str(point.id), point.payload or {}), vec
            if offset is None:
                break

    def _build_filter(self, filters: dict[str, str] | None) -> Filter | None:
        if not filters:
            return None
        must = []
        for key in ("user_id", "agent_id", "run_id"):
            if key in filters:
                must.append(FieldCondition(key=key, match=MatchValue(value=filters[key])))
        return Filter(must=must) if must else None

    def _point_to_record(self, point_id: str, payload: dict) -> MemoryRecord:
        return MemoryRecord(
            id=point_id,
            text=str(payload.get("text", "")),
            scope=MemoryScope(
                user_id=payload.get("user_id"),
                agent_id=payload.get("agent_id"),
                run_id=payload.get("run_id"),
                metadata=payload.get("metadata") or {},
            ),
            entities=list(payload.get("entities") or []),
            source=str(payload.get("source", "conversation")),
            created_at=datetime.fromisoformat(str(payload.get("created_at"))),
        )

    def close(self) -> None:
        self._client.close()