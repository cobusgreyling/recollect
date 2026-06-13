import pytest

from recollect.config import RecollectConfig
from recollect.memory import Memory

pytest.importorskip("langchain_core")

from recollect.integrations.langchain import create_recollect_tools, memory_runnable


@pytest.mark.integration
def test_langchain_tools_and_runnable(tmp_path) -> None:
    config = RecollectConfig.local_dev().model_copy(update={"data_dir": tmp_path / "d"})
    memory = Memory(config)
    memory.add("User drinks oat milk lattes", user_id="alice", infer=False)

    tools = create_recollect_tools(memory, user_id="alice")
    names = {t.name for t in tools}
    assert names == {"search_memory", "save_memory"}

    search_tool = next(t for t in tools if t.name == "search_memory")
    out = search_tool.invoke({"query": "coffee", "top_k": 3})
    assert "oat milk" in out.lower()

    runnable = memory_runnable(memory, user_id="alice")
    payload = runnable.invoke({"input": "coffee preferences"})
    assert "oat milk" in payload["memories"].lower()
    memory.close()
