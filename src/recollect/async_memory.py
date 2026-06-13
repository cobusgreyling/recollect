from __future__ import annotations

import asyncio
from typing import Any

from recollect.config import RecollectConfig
from recollect.memory_core import MemoryCore


class AsyncMemory:
    """Async facade over MemoryCore using thread offloading for store and embed IO."""

    def __init__(self, config: RecollectConfig | None = None) -> None:
        self._core = MemoryCore(config=config)

    async def add(
        self,
        messages: str | list[dict[str, Any]],
        *,
        user_id: str | None = None,
        agent_id: str | None = None,
        run_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        infer: bool = True,
    ) -> dict[str, Any]:
        return await asyncio.to_thread(
            self._core.add,
            messages,
            user_id=user_id,
            agent_id=agent_id,
            run_id=run_id,
            metadata=metadata,
            infer=infer,
        )

    async def search(
        self,
        query: str,
        *,
        filters: dict[str, str] | None = None,
        top_k: int | None = None,
    ) -> dict[str, Any]:
        return await asyncio.to_thread(
            self._core.search,
            query,
            filters=filters,
            top_k=top_k,
        )

    async def get(self, memory_id: str) -> dict[str, Any] | None:
        return await asyncio.to_thread(self._core.get, memory_id)

    async def get_all(self, filters: dict[str, str] | None = None) -> dict[str, Any]:
        return await asyncio.to_thread(self._core.get_all, filters)

    async def delete(self, memory_id: str) -> dict[str, str]:
        return await asyncio.to_thread(self._core.delete, memory_id)

    async def aclose(self) -> None:
        await asyncio.to_thread(self._core.close)

    def close(self) -> None:
        self._core.close()
