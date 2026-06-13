# LangChain integration

Install:

```bash
pip install "recollect[langchain,openai]"
```

## Tools

```python
from recollect import Memory, RecollectConfig
from recollect.integrations.langchain import create_recollect_tools

memory = Memory(RecollectConfig.local_dev())
tools = create_recollect_tools(memory, user_id="alice")
# Pass tools to your LangChain agent executor
```

## Runnable (retrieve before LLM)

```python
from recollect.integrations.langchain import memory_runnable

runnable = memory_runnable(memory, user_id="alice")
payload = runnable.invoke({"input": "What do I prefer?"})
# payload["memories"] is formatted bullet list
```

## Full example

See [`examples/langchain_travel_agent.py`](../../examples/langchain_travel_agent.py) and [`examples/langgraph_memory_node.py`](../../examples/langgraph_memory_node.py).