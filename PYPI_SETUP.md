# PyPI setup (required once)

Publishing failed until PyPI knows this GitHub repo. Pick **one** method.

## Method A — Trusted publishing (recommended)

Create **two** PyPI projects (if they do not exist yet):

1. https://pypi.org/manage/projects/recollect-ai/
2. https://pypi.org/manage/projects/llama-index-memory-recollect/

For **each** project → **Publishing** → **Add a new publisher**:

| Field | Value |
|-------|--------|
| PyPI project name | `recollect-ai` or `llama-index-memory-recollect` |
| Owner | `cobusgreyling` |
| Repository name | `recollect` |
| Workflow name | `publish.yml` |
| Environment name | *(leave empty)* |

Then re-run publish:

```bash
gh workflow run publish.yml -R cobusgreyling/recollect
# or create a new release tag
```

## Method B — API token fallback

```bash
gh secret set PYPI_API_TOKEN --repo cobusgreyling/recollect
# paste pypi-... token with scope for both projects
gh workflow run publish.yml -R cobusgreyling/recollect
```

## Verify

```bash
pip install recollect-ai llama-index-memory-recollect
python -c "import recollect; from llama_index.memory.recollect import RecollectMemory; print('ok')"
```