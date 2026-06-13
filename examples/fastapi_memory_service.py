"""
Tiny FastAPI memory sidecar / microservice example using Recollect.

Demonstrates:
- Scoped add + search over HTTP
- Using RecollectConfig.in_memory() or local SQLite
- Simple Pydantic request/response models

Run:
    pip install "recollect-ai[all]" fastapi uvicorn
    uvicorn examples.fastapi_memory_service:app --reload

Then:
    curl -X POST http://127.0.0.1:8000/memories/add \
      -H 'content-type: application/json' \
      -d '{"text":"Prefers dark theme","user_id":"alice"}'

    curl 'http://127.0.0.1:8000/memories/search?query=dark&user_id=alice'
"""

from __future__ import annotations

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

from recollect import Memory, RecollectConfig

app = FastAPI(title="Recollect Memory Service", version="0.2.1")

# In production you would probably use a singleton + lifespan events + real config
# (e.g. from env: QDRANT_HOST etc). Here we default to fast in-memory for the example.
memory = Memory(RecollectConfig.in_memory())


class AddRequest(BaseModel):
    text: str = Field(..., description="The fact or note to store")
    user_id: str | None = None
    agent_id: str | None = None
    run_id: str | None = None
    infer: bool = Field(
        default=False,
        description="Whether to run LLM extraction (requires OPENAI_API_KEY + config)",
    )


class SearchResponse(BaseModel):
    results: list[dict]


@app.post("/memories/add")
def add_memory(req: AddRequest) -> dict:
    result = memory.add(
        req.text,
        user_id=req.user_id,
        agent_id=req.agent_id,
        run_id=req.run_id,
        infer=req.infer,
    )
    return result


@app.get("/memories/search", response_model=SearchResponse)
def search_memories(
    query: str = Query(..., min_length=1),
    user_id: str | None = None,
    agent_id: str | None = None,
    run_id: str | None = None,
    top_k: int = 5,
) -> dict:
    filters: dict[str, str] = {}
    if user_id:
        filters["user_id"] = user_id
    if agent_id:
        filters["agent_id"] = agent_id
    if run_id:
        filters["run_id"] = run_id

    return memory.search(query, filters=filters or None, top_k=top_k)


@app.get("/memories")
def list_memories(
    user_id: str | None = None,
    agent_id: str | None = None,
    run_id: str | None = None,
) -> dict:
    filters: dict[str, str] = {}
    if user_id:
        filters["user_id"] = user_id
    if agent_id:
        filters["agent_id"] = agent_id
    if run_id:
        filters["run_id"] = run_id
    return memory.get_all(filters=filters or None)


@app.delete("/memories/{memory_id}")
def delete_memory(memory_id: str) -> dict:
    return memory.delete(memory_id)


@app.on_event("shutdown")
def shutdown():
    memory.close()
