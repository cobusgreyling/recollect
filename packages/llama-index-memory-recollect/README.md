# llama-index-memory-recollect

LlamaIndex `BaseMemory` adapter for [Recollect](https://github.com/cobusgreyling/recollect).

```bash
pip install llama-index-memory-recollect
```

```python
from llama_index.memory.recollect import RecollectMemory

memory = RecollectMemory.from_config(
    context={"user_id": "alice"},
    config=RecollectConfig.local_dev(),
)
```