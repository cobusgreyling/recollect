# Publishing

## PyPI (`recollect-ai`)

The PyPI project name is **`recollect-ai`** (the name `recollect` is taken). Python import stays `recollect`.

```bash
pip install build twine
python -m build
twine upload dist/*
```

Or create a GitHub Release to trigger `.github/workflows/publish.yml` (trusted publishing).

## PyPI (`llama-index-memory-recollect`)

```bash
cd packages/llama-index-memory-recollect
python -m build
twine upload dist/*
```

Publish `recollect-ai` first so the dependency resolves.

## LlamaHub

See [LLAMAHUB.md](LLAMAHUB.md). Upstream listing is added via PR to `run-llama/llama_index`.

## GitHub

- Repository topics: `langchain`, `llamaindex`, `ai-agents`, `memory`, `long-term-memory`, `python`
- Enable GitHub Pages from `/docs` when available on your plan.