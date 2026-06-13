# Contributing to Recollect

Thank you for your interest in improving Recollect! We welcome bug reports, feature requests, documentation improvements, and code contributions.

## Development Setup

1. Clone and create a virtual environment (or use your preferred tool):

   ```bash
   git clone https://github.com/cobusgreyling/recollect.git
   cd recollect
   python -m venv .venv
   source .venv/bin/activate   # or `.venv\Scripts\activate` on Windows
   ```

2. Install in editable mode with dev dependencies + the LlamaIndex adapter:

   ```bash
   make install
   # or manually:
   pip install -e ".[dev]"
   pip install -e packages/llama-index-memory-recollect
   ```

3. (Optional) Install everything including vector DB extras for broader testing:

   ```bash
   make install-all
   ```

## Running Tests & Checks

```bash
make test          # pytest (fast with in-memory config)
make lint          # ruff check + format --check
make format        # auto-format
make demo          # quick CLI smoke
```

- Use `RecollectConfig.in_memory()` in new unit tests for speed and isolation.
- Integration tests are marked `@pytest.mark.integration` and use `pytest.importorskip`.
- Coverage is collected automatically via pytest-cov when installed.

Before opening a PR, please ensure:

- `make lint` is clean
- `make test` passes
- New functionality has tests (especially anything touching `retrieval.py`, stores, or scoring)

## Code Style

- We use **ruff** for linting and formatting (configured in `pyproject.toml`).
- Line length: 100.
- Prefer clear, small functions. The retrieval scoring and store Protocol are intentionally easy to read and audit.
- Add type hints where practical. The project ships a `py.typed` marker.

## Adding / Changing a Vector Store

1. Implement the `MemoryStore` protocol (see `src/recollect/stores/base.py`).
2. Add a concrete class (e.g. `my_store.py`).
3. Wire it in `src/recollect/stores/factory.py` and update `VectorStoreConfig.provider` Literal + docs.
4. Add or extend tests (ideally using the real client when available, or mocks).
5. Document the extra in README extras table and `pyproject.toml`.

## Pull Request Process

- Fork the repo and create a feature branch from `main`.
- Keep PRs focused. Small, reviewable diffs are preferred.
- Update `CHANGELOG.md` (Unreleased section) for user-visible changes.
- If docs or examples change, consider whether the interactive showcase (`docs/showcase.html`) or GitHub Pages content needs a matching update.
- CI must be green (lint + test matrix).

## Reporting Issues

Please include:

- Python version + OS
- Exact `pip show recollect-ai` (or source checkout)
- Minimal repro code or steps
- Expected vs actual behavior
- (For retrieval bugs) the query, a couple of memories, and ideally the score breakdown you saw

## Security

See [SECURITY.md](SECURITY.md) for how to report vulnerabilities.

## License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License (same as the project).

Thanks again — Recollect exists to be a small, understandable, powerful memory primitive you can trust inside your agents.
