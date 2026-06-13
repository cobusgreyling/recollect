#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

if [[ -z "${TWINE_PASSWORD:-}" && -z "${PYPI_API_TOKEN:-}" ]]; then
  echo "Set TWINE_PASSWORD or PYPI_API_TOKEN to your PyPI API token."
  exit 1
fi
export TWINE_USERNAME="${TWINE_USERNAME:-__token__}"
export TWINE_PASSWORD="${TWINE_PASSWORD:-$PYPI_API_TOKEN}"

pip install -q build twine
python -m build
twine upload dist/*

python -m build packages/llama-index-memory-recollect
twine upload packages/llama-index-memory-recollect/dist/*

echo "Published recollect-ai and llama-index-memory-recollect"