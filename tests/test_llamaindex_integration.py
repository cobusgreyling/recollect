import pytest

pytest.importorskip("llama_index.core")

from llama_index.core.base.llms.types import ChatMessage, MessageRole
from llama_index.memory.recollect import RecollectMemory

from recollect.config import RecollectConfig


@pytest.mark.integration
def test_recollect_memory_injects_system_message(tmp_path) -> None:
    config = RecollectConfig.local_dev().model_copy(update={"data_dir": tmp_path / "d"})
    memory = RecollectMemory.from_config(context={"user_id": "bob"}, config=config)
    assert memory._client is not None
    memory._client.add("User lives in Cape Town", user_id="bob", infer=False)

    memory.primary_memory.put(ChatMessage(role=MessageRole.USER, content="Where do I live?"))
    messages = memory.get(input="Where do I live?")
    assert messages[0].role == MessageRole.SYSTEM
    assert "Cape Town" in (messages[0].content or "")
