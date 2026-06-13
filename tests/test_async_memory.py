import pytest

from recollect.async_memory import AsyncMemory
from recollect.config import RecollectConfig


@pytest.mark.asyncio
async def test_async_add_search(tmp_path) -> None:
    config = RecollectConfig.local_dev().model_copy(update={"data_dir": tmp_path / "d"})
    mem = AsyncMemory(config)
    await mem.add("Loves TypeScript", user_id="u1", infer=False)
    hits = await mem.search("programming language", filters={"user_id": "u1"})
    assert hits["results"]
    await mem.aclose()