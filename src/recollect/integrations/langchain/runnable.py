from __future__ import annotations

from typing import Any

from langchain_core.runnables import Runnable, RunnableLambda
from langchain_core.runnables.config import RunnableConfig

from recollect.integrations.langchain.tools import format_memories_for_prompt
from recollect.memory import Memory


class RecollectRunnable(Runnable):
    """Retrieve memories for a user message and attach them to the payload."""

    def __init__(
        self,
        memory: Memory,
        *,
        user_id: str,
        agent_id: str | None = None,
        run_id: str | None = None,
        top_k: int = 5,
        memory_key: str = "memories",
    ) -> None:
        self.memory = memory
        self.user_id = user_id
        self.agent_id = agent_id
        self.run_id = run_id
        self.top_k = top_k
        self.memory_key = memory_key

    def _filters(self) -> dict[str, str]:
        flt: dict[str, str] = {"user_id": self.user_id}
        if self.agent_id:
            flt["agent_id"] = self.agent_id
        if self.run_id:
            flt["run_id"] = self.run_id
        return flt

    def invoke(self, input: dict[str, Any], config: RunnableConfig | None = None) -> dict[str, Any]:
        message = input.get("input") or input.get("message") or ""
        hits = self.memory.search(str(message), filters=self._filters(), top_k=self.top_k)
        return {**input, self.memory_key: format_memories_for_prompt(hits), "memory_hits": hits}

    async def ainvoke(
        self, input: dict[str, Any], config: RunnableConfig | None = None
    ) -> dict[str, Any]:
        return self.invoke(input, config)


def memory_runnable(
    memory: Memory,
    *,
    user_id: str,
    agent_id: str | None = None,
    run_id: str | None = None,
    top_k: int = 5,
) -> RunnableLambda:
    runner = RecollectRunnable(
        memory,
        user_id=user_id,
        agent_id=agent_id,
        run_id=run_id,
        top_k=top_k,
    )
    return RunnableLambda(runner.invoke)
