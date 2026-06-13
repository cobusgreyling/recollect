# Publishing

## PyPI (recollect)

```bash
pip install build twine
python -m build
twine upload dist/*
```

Set `PYPI_API_TOKEN` or use `twine login`.

## PyPI (llama-index-memory-recollect)

```bash
cd packages/llama-index-memory-recollect
python -m build
twine upload dist/*
```

Publish `recollect` first so the dependency resolves.

## GitHub

- Repository topics: `langchain`, `llamaindex`, `ai-agents`, `memory`, `long-term-memory`, `python`
- Enable GitHub Pages from `/docs` when available on your plan.