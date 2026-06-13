# Production & Scale Notes

Recollect is designed to be simple and embeddable. Here are practical considerations when moving beyond prototypes.

## Choosing a Backend

| Backend   | Best for                          | Notes / Caveats                              | Persistence |
|-----------|-----------------------------------|----------------------------------------------|-------------|
| `memory`  | Unit tests, benchmarks, ephemeral | Zero disk/IO. Data gone on restart.          | None        |
| `sqlite`  | Most apps, local dev, small SaaS  | Default. Good up to low tens/hundreds of thousands of memories on a single node. | File        |
| `chroma`  | Local vector experimentation      | Easy persistent local dir.                   | Local dir   |
| `qdrant`  | Production self-hosted            | Excellent filtering + performance. Run via Docker. | Server      |
| `pgvector`| Existing Postgres users           | Use when you already have Postgres + pgvector extension. | Server (DB) |

For anything beyond ~100k memories or high QPS, move to Qdrant or pgvector and monitor query latency on `iter_with_embeddings` (current implementation loads candidates for the scope into memory for hybrid fusion).

## Scoping & Multi-Tenancy

Always supply at least one of `user_id`, `agent_id`, or `run_id` in production. This keeps result sets small and predictable.

```python
memory.add(..., user_id=customer_id, agent_id="support-bot-v3")
hits = memory.search(q, filters={"user_id": customer_id})
```

You can also store extra information in `metadata={...}` on add (it is returned in search hit metadata).

## Extraction (LLM fact pulling)

- `extraction_enabled=True` (default) + valid `OPENAI_API_KEY` will call the LLM on every `add(..., infer=True)`.
- Cost & latency: each `add` of a multi-turn conversation can trigger one LLM call.
- For high-volume paths, prefer `infer=False` + your own extraction / summarization, or batch facts yourself.
- The system prompt favors stable, atomic, third-person facts. Tweak by subclassing `FactExtractor` if needed.

## Embeddings

- `local` (default in `local_dev()` / `in_memory()`): fast, deterministic, zero-dep, low quality. Good for tests & demos. Dimension is tiny (64 by default).
- `huggingface`: good quality local models (sentence-transformers). Requires the extra.
- `openai` / `ollama`: production quality. Set `dimensions` to control cost / index size.
- All embeddings are L2-normalized internally before storage and cosine is used.

**Recommendation**: Start with `local` or a small HF model for prototyping. Switch to OpenAI `text-embedding-3-small` (or your org's preferred) for production relevance.

## Observability & Debugging

- Retrieval hits include a `metadata` dict with `semantic`, `keyword`, `entity_overlap` (and any scope metadata). Log or surface these during development.
- Basic `logging.getLogger("recollect")` debug logs are emitted from the core add/search paths (enable with `logging.basicConfig(level=logging.DEBUG)` or your app's logging config).
- For production, wrap calls and record: scope, query, #candidates, top score, latency.

## Limits & Performance Tips

- The hybrid fusion currently iterates all candidates for the filtered scope and scores in Python. This is simple, correct, and great for < 50k memories per scope.
- To scale further:
  - Use a vector DB that can do server-side hybrid (Qdrant supports this well; you can later add a "hybrid" path that uses server-side keyword + vector).
  - Periodically consolidate / summarize old memories (your own background job calling `get_all` + LLM + re-add + delete).
  - Consider time-based decay or importance scores as an additional fusion signal (easy to add on top of `SearchHit`).
- Close stores (`memory.close()`) when you are done with a `Memory` instance in long-running processes (important for pgvector / some clients).

## Backups & Data Portability

- SQLite: just copy the `~/.recollect/memories.db` (or your configured path).
- Other stores: use the vendor tools (pg_dump, Qdrant snapshots, Chroma export, etc.).
- You can always `get_all()` everything for a scope and re-ingest into another backend (the `add(..., infer=False)` path makes this lossless for raw facts).

## Security

- Never commit real `OPENAI_API_KEY` or production DSNs.
- When using `pgvector`, use connection strings with limited users and SSL where possible.
- Memory contents are stored in plaintext in the backing store. Apply your own encryption at rest / column-level if you have strict PII/compliance requirements.

## Monitoring Checklist

- Track p95 search latency per scope size.
- Alert on extraction LLM error rates / cost.
- Watch SQLite file size / wal growth if using WAL mode.
- For Qdrant/pgvector: index build time, memory usage, collection sizes.

Recollect tries hard to stay out of your way. When you outgrow the current simple "load + fuse in Python" approach, the clean store abstraction and typed records make it straightforward to evolve or swap in a heavier retrieval engine while keeping the same `Memory` / `AsyncMemory` surface for your agents.
