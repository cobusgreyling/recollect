# Recollect

![Recollect header — memory, books, and time](docs/assets/header.jpg)

**🌐 [Live Demo](https://cobusgreyling.github.io/recollect/)** · **[Interactive Showcase](https://cobusgreyling.github.io/recollect/showcase.html)** · **[LangChain](docs/integrations/langchain.md)** · **[LlamaIndex](docs/integrations/llama-index.md)**

> **The showcase on this page is raw code.**  
> For the real interactive presentation (add memories, hybrid search, chat simulation), go to the **live site** above.

Long-term **memory layer** for AI agents and assistants—self-hosted, **library-first**, and integration-ready for **LangChain** and **LlamaIndex** OSS workflows. Small, embeddable, and transparent.

## Why Recollect

- **ADD-only facts** from conversations (optional LLM extraction)
- **Scoped memory** — `user_id`, `agent_id`, `run_id`
- **Hybrid retrieval** — semantic + keyword + entity boost
- **Pluggable stores** — SQLite (default), Qdrant, Chroma, pgvector
- **No platform required** — embed in your app; open Apache 2.0

### Why Recollect vs alternatives?

Recollect is a **small, embeddable library** (not a platform or hosted service). Key differentiators:

- **Transparent & debuggable retrieval**: `search` returns per-result `metadata` with `semantic`, `keyword`, and `entity_overlap` scores so you can see exactly why a memory ranked high.
- **Best-in-class local developer experience**: `RecollectConfig.local_dev()` gives you a fully working memory layer with **zero API keys**, using a fast deterministic local embedder + SQLite. Perfect for tests, demos, and CI.
- **Strong multi-tenancy by design**: Every memory is partitioned by `user_id` / `agent_id` / `run_id` (and arbitrary metadata). Great for SaaS, multi-agent, or per-conversation isolation.
- **Framework-native, not framework-heavy**: Real (not toy) integrations for LangChain (tools + Runnable) and LlamaIndex (`BaseMemory`). Drop it into existing graphs/agents with minimal glue.
- **Self-host everything**: Your data, your infra choices (or SQLite file on disk). No usage-based billing surprises.
- **Tiny and auditable**: Minimal core dependencies. Apache 2.0. Easy to read the retrieval logic and adapt.

If you want a batteries-included cloud memory service with lots of bells and graphs, look at Mem0 or Zep. If you want a **focused, controllable, library-first** long-term memory layer you can understand and ship inside your own code, Recollect is built for you.

## Install

**From PyPI (recommended for usage):**

```bash
pip install recollect-ai
pip install llama-index-memory-recollect   # optional LlamaIndex adapter
```

**From source (for development or latest):**

```bash
git clone https://github.com/cobusgreyling/recollect.git
cd recollect
pip install -e ".[dev]"
pip install -e packages/llama-index-memory-recollect
```

### Extras

| Extra | Purpose |
|-------|---------|
| `openai` | OpenAI LLM + embeddings |
| `langchain` | Tools + Runnable helpers |
| `llamaindex` | Core types for LlamaIndex apps |
| `qdrant` / `chroma` / `pgvector` | Vector backends |
| `huggingface` | HF sentence-transformers embedder |
| `all` | Everything |

## 5-minute local demo (no API keys)

```bash
pip install -e .
recollect demo
```

```python
from recollect import Memory, RecollectConfig

memory = Memory(RecollectConfig.local_dev())
memory.add("Prefers PostgreSQL over MySQL", user_id="alice", infer=False)
print(memory.search("database", filters={"user_id": "alice"}))
```

## LangChain

```python
from recollect import Memory, RecollectConfig
from recollect.integrations.langchain import create_recollect_tools, memory_runnable

memory = Memory(RecollectConfig.local_dev())
tools = create_recollect_tools(memory, user_id="alice")
ctx = memory_runnable(memory, user_id="alice").invoke({"input": "database prefs"})
```

Examples: [`examples/langchain_travel_agent.py`](examples/langchain_travel_agent.py), [`examples/langgraph_memory_node.py`](examples/langgraph_memory_node.py), [`examples/fastapi_memory_service.py`](examples/fastapi_memory_service.py) (HTTP sidecar), [`examples/chat_with_memory.py`](examples/chat_with_memory.py)

## LlamaIndex

```python
from llama_index.memory.recollect import RecollectMemory
from recollect.config import RecollectConfig

memory = RecollectMemory.from_config(
    context={"user_id": "alice"},
    config=RecollectConfig.local_dev(),
)
# SimpleChatEngine.from_defaults(llm=llm, memory=memory)
```

Package: [`packages/llama-index-memory-recollect`](packages/llama-index-memory-recollect)

## API

| Method | Purpose |
|--------|---------|
| `add(...)` | Extract/store memories |
| `search(query, filters={}, top_k=5)` | Hybrid retrieval |
| `get` / `get_all` / `delete` | CRUD |

`AsyncMemory` provides the same API with `async`/`await`.

See [Production & Scale notes](docs/production-and-scale.md) for backend choice, performance characteristics, extraction cost considerations, and operational guidance.

## Development

```bash
make install
make test
make lint
make demo
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## Roadmap

- [x] LangChain tools + Runnable
- [x] LlamaIndex `RecollectMemory`
- [x] Async API, multi-backend stores
- [x] Ruff linting + formatting, expanded tests, InMemoryStore, basic logging, robust stores
- [x] LlamaHub listing documentation + standalone PyPI packages
- [ ] Full LangGraph + production cookbook examples
- [ ] Upstream LlamaIndex docs notebook PR
- [ ] Optional graph / entity relationship layer (future)
- [ ] Public recall quality benchmarks / evals harness

## 🌐 Live Interactive Showcase (recommended)

The best way to experience Recollect is the **fully interactive browser demo**:

→ **https://cobusgreyling.github.io/recollect/showcase.html**

It includes:
- Live **add memory** form with full scoping (`user_id`, `agent_id`, `run_id`)
- **Hybrid search lab** that shows semantic + keyword + entity scores (mirrors the Python implementation)
- **Chat simulation** — retrieve memories, get a simulated reply, and write the exchange back

Everything runs 100% in your browser using the same local-embedder + hybrid retrieval logic as the library. Data stays in your `localStorage`.

(The links to `docs/showcase.html` and `docs/index.html` in this README point at the **source code** on GitHub, which is why it looks like “just code”. The real presentation is at the link above.)

## Acknowledgments

Patterns draw on public agent-memory research and OSS work, including additive extraction and multi-signal retrieval popularized by [Mem0](https://github.com/mem0ai/mem0). Recollect is an independent codebase.

## License

Apache 2.0 — see [LICENSE](LICENSE).