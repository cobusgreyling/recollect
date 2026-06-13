# Publishing

## PyPI (`recollect-ai`)

The PyPI project name is **`recollect-ai`** (the name `recollect` is taken). Python import stays `recollect`.

Local one-off:

```bash
pip install build
python -m build
```

**Best**: Push a GitHub Release (or manually trigger the "Publish to PyPI" workflow). This runs `.github/workflows/publish.yml`.

The workflow uses the official PyPA publish action. It:
- Automatically uses **Trusted Publishing (OIDC)** if you configure the GitHub repo as a trusted publisher on PyPI (recommended — no secrets).
- Falls back to `secrets.PYPI_API_TOKEN` (create an API token on PyPI with upload scope for both packages).

## PyPI (`llama-index-memory-recollect`)

The workflow has a dependent job for it (it waits for `recollect-ai` because of the version pin in its `pyproject.toml`).

Or manually in the subdir:

```bash
cd packages/llama-index-memory-recollect
python -m build
```

Publish `recollect-ai` first so the dependency resolves.

## LlamaHub

See any LLAMAHUB.md if present. Upstream listing usually requires a separate PR to `run-llama/llama_index`.

## GitHub

- Topics: `langchain`, `llamaindex`, `ai-agents`, `memory`, `long-term-memory`, `python`
- GitHub Pages serves the interactive demo (`docs/` folder on `main`): https://cobusgreyling.github.io/recollect/showcase.html

## CI notes

Pushes/PRs to `main` run tests on Python 3.10 and 3.12. Only non-`@pytest.mark.integration` tests run by default. The integration tests for the LangChain and LlamaIndex adapters require the optional deps.