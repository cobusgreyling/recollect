from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path

import numpy as np

from recollect.types import MemoryRecord, MemoryScope


class SQLiteMemoryStore:
    """SQLite-backed memory store with embedding vectors stored as JSON blobs."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                user_id TEXT,
                agent_id TEXT,
                run_id TEXT,
                entities TEXT NOT NULL,
                metadata TEXT NOT NULL,
                source TEXT NOT NULL,
                created_at TEXT NOT NULL,
                embedding TEXT NOT NULL
            )
            """
        )
        self._conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_user ON memories(user_id)")
        self._conn.commit()

    def insert(self, record: MemoryRecord, embedding: np.ndarray) -> None:
        scope = record.scope
        self._conn.execute(
            """
            INSERT INTO memories (
                id, text, user_id, agent_id, run_id, entities, metadata,
                source, created_at, embedding
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                record.created_at.isoformat(),
                json.dumps(embedding.astype(np.float32).tolist()),
            ),
        )
        self._conn.commit()

    def delete(self, memory_id: str) -> bool:
        cur = self._conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        self._conn.commit()
        return cur.rowcount > 0

    def get(self, memory_id: str) -> MemoryRecord | None:
        row = self._conn.execute("SELECT * FROM memories WHERE id = ?", (memory_id,)).fetchone()
        if not row:
            return None
        return self._row_to_record(row)

    def list_all(self, filters: dict[str, str] | None = None) -> list[MemoryRecord]:
        query = "SELECT * FROM memories"
        params: list[str] = []
        if filters:
            clauses = []
            for key in ("user_id", "agent_id", "run_id"):
                if key in filters:
                    clauses.append(f"{key} = ?")
                    params.append(filters[key])
            if clauses:
                query += " WHERE " + " AND ".join(clauses)
        rows = self._conn.execute(query, params).fetchall()
        return [self._row_to_record(r) for r in rows]

    def iter_with_embeddings(
        self, filters: dict[str, str] | None = None
    ) -> Iterable[tuple[MemoryRecord, np.ndarray]]:
        query = "SELECT * FROM memories"
        params: list[str] = []
        if filters:
            clauses = []
            for key in ("user_id", "agent_id", "run_id"):
                if key in filters:
                    clauses.append(f"{key} = ?")
                    params.append(filters[key])
            if clauses:
                query += " WHERE " + " AND ".join(clauses)
        for row in self._conn.execute(query, params):
            record = self._row_to_record(row)
            emb = np.array(json.loads(row["embedding"]), dtype=np.float32)
            yield record, emb

    def _row_to_record(self, row: sqlite3.Row) -> MemoryRecord:
        return MemoryRecord(
            id=row["id"],
            text=row["text"],
            scope=MemoryScope(
                user_id=row["user_id"],
                agent_id=row["agent_id"],
                run_id=row["run_id"],
                metadata=json.loads(row["metadata"] or "{}"),
            ),
            entities=json.loads(row["entities"] or "[]"),
            source=row["source"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def close(self) -> None:
        self._conn.close()
