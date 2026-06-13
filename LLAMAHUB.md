# LlamaHub listing

LlamaHub indexes integration packages from the [LlamaIndex monorepo](https://github.com/run-llama/llama_index) that declare `[tool.llamahub]` in `pyproject.toml`.

## Steps

1. **Publish `recollect-ai` to PyPI** (import remains `recollect`).
2. **Publish `llama-index-memory-recollect` to PyPI** (or merge the upstream LlamaIndex PR).
3. After the LlamaIndex PR merges, docs CI runs `docs/scripts/prepare_for_build.py`, which registers the integration API reference and LlamaHub metadata.
4. Install from LlamaHub:

```bash
pip install llama-index-memory-recollect recollect-ai
```

Hub URL (once indexed): `https://llamahub.ai/l/memory/llama-index-memory-recollect`