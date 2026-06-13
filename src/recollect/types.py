from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MemoryScope(BaseModel):
    """Scopes memories to a user, agent, session, or custom partition."""

    user_id: str | None = None
    agent_id: str | None = None
    run_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    def as_filters(self) -> dict[str, str]:
        out: dict[str, str] = {}
        if self.user_id:
            out["user_id"] = self.user_id
        if self.agent_id:
            out["agent_id"] = self.agent_id
        if self.run_id:
            out["run_id"] = self.run_id
        return out


class MemoryRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    text: str
    scope: MemoryScope = Field(default_factory=MemoryScope)
    entities: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    source: str = "conversation"

    def matches_filters(self, filters: dict[str, str]) -> bool:
        scope = self.scope.as_filters()
        return all(scope.get(key) == value for key, value in filters.items())


class SearchHit(BaseModel):
    id: str
    memory: str
    score: float
    created_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)
