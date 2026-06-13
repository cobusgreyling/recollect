.PHONY: install install-all test demo lint format lint-fix

install:
	pip install -e ".[dev]"
	pip install -e packages/llama-index-memory-recollect

install-all:
	pip install -e ".[all,dev]"
	pip install -e packages/llama-index-memory-recollect

test:
	pytest -q

demo:
	recollect demo --user-id demo_user --query "food and editor preferences"

lint:
	ruff check src packages/llama-index-memory-recollect/src tests
	ruff format --check src packages/llama-index-memory-recollect/src tests

format:
	ruff format src packages/llama-index-memory-recollect/src tests

lint-fix:
	ruff check --fix src packages/llama-index-memory-recollect/src tests
	ruff format src packages/llama-index-memory-recollect/src tests

# Legacy fallback
compile-check:
	python -m compileall -q src packages/llama-index-memory-recollect/src