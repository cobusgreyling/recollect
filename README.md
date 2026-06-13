# Recollect

Long-term memory layer for AI agents and assistants. Recollect turns conversations into durable facts, scopes them per user/agent/session, and retrieves the right context with semantic + keyword + entity signals.

## Why

Stateful agents need memory that survives a single context window: preferences, constraints, past outcomes, and confirmed actions. Recollect gives you a small, embeddable library for that workflow without tying you to a hosted platform.

## Features

- **ADD-only extraction** — accumulate atomic facts from chat (optional LLM extraction)
- **Scoped memory** — `user_id`, `agent_id`, `run_id` filters
- **Hybrid retrieval** — embedding similarity, BM25-style keyword scoring, entity overlap boost
- **Local-first storage** — SQLite under `~/.recollect` (configurable)
- **Pluggable embedders** — OpenAI embeddings or deterministic local vectors for dev/tests

## Install

```bash
cd recollect
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Quickstart

```python
from recollect import Memory, RecollectConfig
from recollect.config import EmbedderConfig

memory = Memory(
    RecollectConfig(
        extraction_enabled=False,
        embedder=EmbedderConfig(provider="local"),
    )
)

memory.add("Prefers PostgreSQL over MySQL", user_id="alice", infer=False)
results = memory.search("database preference", filters={"user_id": "alice"})
print(results["results"][0]["memory"])
```

With OpenAI extraction and embeddings, set `OPENAI_API_KEY` and use default config:

```python
from recollect import Memory

memory = Memory()
memory.add(
    [
        {"role": "user", "content": "I moved to Berlin last month."},
        {"role": "assistant", "content": "Noted — I'll remember you're in Berlin."},
    ],
    user_id="alice",
)
```

See `examples/chat_with_memory.py` for a full REPL-style integration.

## API

| Method | Purpose |
|--------|---------|
| `add(messages, user_id=..., infer=True)` | Extract and store memories |
| `search(query, filters={}, top_k=5)` | Hybrid retrieval |
| `get(memory_id)` | Fetch one record |
| `get_all(filters={})` | List scoped memories |
| `delete(memory_id)` | Remove a memory |

## Roadmap

- [ ] Async API and batch embedding
- [ ] Vector store backends (Qdrant, pgvector)
- [ ] Temporal ranking for time-sensitive facts
- [ ] HTTP server and dashboard
- [ ] TypeScript SDK

## Development

```bash
pytest
```

## Acknowledgments

Design ideas draw on public research and open work in agent memory systems, including additive fact extraction and multi-signal retrieval patterns popularized by projects such as [Mem0](https://github.com/mem0ai/mem0) and their [research paper](https://arxiv.org/abs/2504.19413). Recollect is an independent implementation and codebase.

## License

Apache 2.0 — see [LICENSE](LICENSE).