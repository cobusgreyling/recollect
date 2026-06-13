# Recollect

![Recollect header — memory, books, and time](docs/assets/header.jpg)

**🌐 [Live Demo](https://cobusgreyling.github.io/recollect/)** · **[Interactive Showcase](https://cobusgreyling.github.io/recollect/showcase.html)** · **[LangChain](docs/integrations/langchain.md)** · **[LlamaIndex](docs/integrations/llama-index.md)**

> **The showcase on this page is raw code.**  
> For the real interactive presentation (add memories, hybrid search, chat simulation), go to the **live site** above.

Long-term **memory layer** for AI agents and assistants—self-hosted, library-first, and integration-ready for **LangChain** and **LlamaIndex** OSS workflows.

## Why Recollect

- **ADD-only facts** from conversations (optional LLM extraction)
- **Scoped memory** — `user_id`, `agent_id`, `run_id`
- **Hybrid retrieval** — semantic + keyword + entity boost
- **Pluggable stores** — SQLite (default), Qdrant, Chroma, pgvector
- **No platform required** — embed in your app; open Apache 2.0

## Install

```bash
git clone https://github.com/cobusgreyling/recollect.git
cd recollect
pip install -e ".[dev]"
pip install -e packages/llama-index-memory-recollect   # LlamaIndex adapter
```

PyPI (package name **`recollect-ai`**, import **`recollect`**):

```bash
pip install recollect-ai
pip install llama-index-memory-recollect
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

Examples: [`examples/langchain_travel_agent.py`](examples/langchain_travel_agent.py), [`examples/langgraph_memory_node.py`](examples/langgraph_memory_node.py)

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

## Development

```bash
make install
make test
make demo
```

## Roadmap

- [x] LangChain tools + Runnable
- [x] LlamaIndex `RecollectMemory`
- [x] Async API, multi-backend stores
- [ ] LlamaHub listing + upstream LlamaIndex notebook PR
- [ ] LangGraph cookbook in docs site

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