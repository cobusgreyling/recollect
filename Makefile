.PHONY: install install-all test demo lint

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
	python -m compileall -q src packages/llama-index-memory-recollect/src