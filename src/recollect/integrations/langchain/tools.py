from __future__ import annotations

from typing import Any

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from recollect.memory import Memory


class SearchMemoryInput(BaseModel):
    query: str = Field(description="Natural language query to find relevant user memories")
    top_k: int = Field(default=5, description="Maximum memories to return")


class SaveMemoryInput(BaseModel):
    text: str = Field(description="Fact or note to store as long-term memory")


def create_recollect_tools(
    memory: Memory,
    *,
    user_id: str,
    agent_id: str | None = None,
    run_id: str | None = None,
) -> list[StructuredTool]:
    scope = {"user_id": user_id}
    if agent_id:
        scope["agent_id"] = agent_id
    if run_id:
        scope["run_id"] = run_id
    filters = {k: v for k, v in scope.items() if v is not None}

    def search_memory(query: str, top_k: int = 5) -> str:
        result = memory.search(query, filters=filters, top_k=top_k)
        lines = [f"- {hit['memory']} (score={hit['score']:.3f})" for hit in result["results"]]
        return "\n".join(lines) if lines else "No relevant memories found."

    def save_memory(text: str) -> str:
        out = memory.add(text, infer=False, **scope)
        count = len(out.get("results", []))
        return f"Saved {count} memory record(s)."

    return [
        StructuredTool.from_function(
            func=search_memory,
            name="search_memory",
            description="Search long-term memory for facts about the user or session.",
            args_schema=SearchMemoryInput,
        ),
        StructuredTool.from_function(
            func=save_memory,
            name="save_memory",
            description="Persist a durable fact into long-term memory.",
            args_schema=SaveMemoryInput,
        ),
    ]


def format_memories_for_prompt(search_result: dict[str, Any]) -> str:
    return "\n".join(f"- {r['memory']}" for r in search_result.get("results", []))