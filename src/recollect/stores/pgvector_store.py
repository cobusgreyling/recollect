from __future__ import annotations

import json
from collections.abc import Iterable
from datetime import datetime

import numpy as np

from recollect.config import VectorStoreConfig
from recollect.types import MemoryRecord, MemoryScope


class PgVectorMemoryStore:
    def __init__(self, config: VectorStoreConfig) -> None:
        import psycopg
        from pgvector.psycopg import register_vector

        if not config.pg_dsn:
            raise ValueError("pgvector store requires vector_store.pg_dsn")
        self._dims = config.embedding_dims
        self._conn = psycopg.connect(config.pg_dsn)
        register_vector(self._conn)
        self._init_schema()

    def _init_schema(self) -> None:
        with self._conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS recollect_memories (
                    id TEXT PRIMARY KEY,
                    text TEXT NOT NULL,
                    user_id TEXT,
                    agent_id TEXT,
                    run_id TEXT,
                    entities JSONB NOT NULL DEFAULT '[]',
                    metadata JSONB NOT NULL DEFAULT '{{}}',
                    source TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL,
                    embedding vector({self._dims}) NOT NULL
                )
                """
            )
        self._conn.commit()

    def insert(self, record: MemoryRecord, embedding: np.ndarray) -> None:
        scope = record.scope
        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO recollect_memories (
                    id, text, user_id, agent_id, run_id, entities, metadata,
                    source, created_at, embedding
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (id) DO UPDATE SET
                    text = EXCLUDED.text,
                    embedding = EXCLUDED.embedding
                """,
                (
                    record.id,
                    record.text,
                    scope.user_id,
                    scope.agent_id,
                    scope.run_id,
                    json.dumps(record.entities),
                    json.dumps(scope.metadata),
                    record.source,
                    record.created_at,
                    embedding.tolist(),
                ),
            )
        self._conn.commit()

    def delete(self, memory_id: str) -> bool:
        with self._conn.cursor() as cur:
            cur.execute("DELETE FROM recollect_memories WHERE id = %s", (memory_id,))
            deleted = cur.rowcount > 0
        self._conn.commit()
        return deleted

    def get(self, memory_id: str) -> MemoryRecord | None:
        with self._conn.cursor() as cur:
            cur.execute("SELECT * FROM recollect_memories WHERE id = %s", (memory_id,))
            row = cur.fetchone()
        if not row:
            return None
        return self._row_to_record(row)

    def list_all(self, filters: dict[str, str] | None = None) -> list[MemoryRecord]:
        query = "SELECT * FROM recollect_memories"
        params: list[str] = []
        if filters:
            clauses = []
            for key in ("user_id", "agent_id", "run_id"):
                if key in filters:
                    clauses.append(f"{key} = %s")
                    params.append(filters[key])
            if clauses:
                query += " WHERE " + " AND ".join(clauses)
        with self._conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
        return [self._row_to_record(r) for r in rows]

    def iter_with_embeddings(
        self, filters: dict[str, str] | None = None
    ) -> Iterable[tuple[MemoryRecord, np.ndarray]]:
        for record in self.list_all(filters):
            with self._conn.cursor() as cur:
                cur.execute(
                    "SELECT embedding FROM recollect_memories WHERE id = %s",
                    (record.id,),
                )
                row = cur.fetchone()
            if row:
                emb = np.array(row[0], dtype=np.float32)
                yield record, emb

    def _row_to_record(self, row: tuple) -> MemoryRecord:
        (
            rid,
            text,
            user_id,
            agent_id,
            run_id,
            entities,
            metadata,
            source,
            created_at,
            _embedding,
        ) = row
        return MemoryRecord(
            id=rid,
            text=text,
            scope=MemoryScope(
                user_id=user_id,
                agent_id=agent_id,
                run_id=run_id,
                metadata=metadata if isinstance(metadata, dict) else json.loads(metadata or "{}"),
            ),
            entities=entities if isinstance(entities, list) else json.loads(entities or "[]"),
            source=source,
            created_at=created_at
            if isinstance(created_at, datetime)
            else datetime.fromisoformat(str(created_at)),
        )

    def close(self) -> None:
        self._conn.close()
