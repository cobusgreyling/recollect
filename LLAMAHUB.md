# LlamaHub listing

LlamaIndex **no longer accepts new integration packages** in the monorepo (see [closed PR #21954](https://github.com/run-llama/llama_index/pull/21954)). Recollect ships as **standalone PyPI packages** with `[tool.llamahub]` metadata in `packages/llama-index-memory-recollect/pyproject.toml`.

## Steps

1. **Publish `recollect-ai` to PyPI** — see [PYPI_SETUP.md](PYPI_SETUP.md).
2. **Publish `llama-index-memory-recollect` to PyPI** (same workflow).
3. **Docs notebook PR** (no monorepo package): https://github.com/run-llama/llama_index/pull/new/cobusgreyling:docs/recollect-memory-notebook
4. Install:

```bash
pip install llama-index-memory-recollect recollect-ai
```

Developers discover the integration via PyPI, the [Recollect docs](https://github.com/cobusgreyling/recollect), and the LlamaIndex memory examples list after the docs PR merges.