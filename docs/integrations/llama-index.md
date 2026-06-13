# LlamaIndex integration

Install the adapter package:

```bash
pip install recollect llama-index-memory-recollect
```

From this monorepo:

```bash
pip install -e .
pip install -e packages/llama-index-memory-recollect
```

## RecollectMemory

```python
from llama_index.memory.recollect import RecollectMemory
from recollect.config import RecollectConfig

memory = RecollectMemory.from_config(
    context={"user_id": "alice"},
    config=RecollectConfig.local_dev(),
    search_msg_limit=4,
)
```

Use with `SimpleChatEngine`, `FunctionAgent`, or `ReActAgent` by passing `memory=memory`.

## Example

[`examples/llamaindex_chat_engine.py`](../../examples/llamaindex_chat_engine.py)

## LlamaHub

Upstream PR (LlamaIndex monorepo + `[tool.llamahub]` metadata):

https://github.com/run-llama/llama_index/pull/21954

After merge and PyPI publish:

```bash
pip install llama-index-memory-recollect recollect-ai
```

See [LLAMAHUB.md](../../LLAMAHUB.md).