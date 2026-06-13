from __future__ import annotations

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


@pytest.mark.asyncio
async def test_async_full_crud_inmemory():
    """Async + in-memory combo is great for fast tests."""
    mem = AsyncMemory(RecollectConfig.in_memory())
    await mem.add("Async fact about Rust", user_id="rustacean", infer=False)
    got = await mem.get_all(filters={"user_id": "rustacean"})
    assert len(got["results"]) == 1

    first_id = got["results"][0]["id"]
    fetched = await mem.get(first_id)
    assert fetched and "Rust" in fetched["memory"]

    del_res = await mem.delete(first_id)
    assert del_res["message"] == "deleted"
    assert await mem.get(first_id) is None
    await mem.aclose()
