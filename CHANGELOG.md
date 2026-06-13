# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- InMemoryStore (provider="memory") for fast tests, benchmarks, and ephemeral usage. `RecollectConfig.in_memory()`.
- Comprehensive hybrid retrieval unit tests (`tests/test_retrieval.py`).
- Expanded core + async tests (get_all, filters, CRUD edges, parametrized fixtures).
- Basic structured logging (debug) in MemoryCore for add/search.
- `recollect --version` CLI flag and improved parser.
- Ruff lint + format configuration + `make lint` / `make format` / `make lint-fix`.
- `py.typed` marker (PEP 561) for type checker support.
- `pytest-cov` integration in dev extras and CI.
- Improved delete accuracy + robustness in Chroma and Qdrant stores.
- `RecollectConfig.in_memory()` convenience constructor.
- This CHANGELOG, CONTRIBUTING.md, and SECURITY.md.

### Changed
- Version bump consistency (src and packages now aligned at 0.2.1).
- pyproject dev dependencies expanded (ruff, cov).
- Makefile lint target now uses ruff (with legacy compile-check target).
- CI now has dedicated `lint` job + improved test matrix, smoke demo, coverage.
- README significantly improved: "Why Recollect vs alternatives" comparison, clearer install, updated roadmap, development instructions.
- LlamaIndex integration package version aligned to 0.2.1 and recollect-ai dep tightened.

### Fixed
- `__version__` in package `__init__.py` was out of sync with pyproject (now 0.2.1).
- Minor robustness in vector store delete paths.

## [0.2.1] - 2026-06-13

### Changed
- Publishing and CI improvements (trusted publishing docs + pypa action).
- Docs polish around live showcase vs raw source.

## [0.2.0] - 2026-06

### Added
- LangChain integration (tools + Runnable / memory_runnable).
- LlamaIndex `RecollectMemory` adapter (standalone PyPI package `llama-index-memory-recollect`).
- AsyncMemory facade.
- Multiple vector backends (Qdrant, Chroma, pgvector) + pluggable store architecture.
- Interactive browser-based GitHub Pages showcase with faithful hybrid search simulation.
- CLI (`recollect demo`).
- Full scoped memory (user/agent/run), hybrid retrieval, entity extraction, local embedder.

[0.2.1]: https://github.com/cobusgreyling/recollect/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/cobusgreyling/recollect/releases/tag/v0.2.0
