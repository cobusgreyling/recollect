from pathlib import Path

import pytest

from recollect.config import RecollectConfig
from recollect.memory import Memory


@pytest.fixture
def memory(tmp_path: Path) -> Memory:
    config = RecollectConfig.local_dev()
    config = config.model_copy(update={"data_dir": tmp_path / "data"})
    mem = Memory(config)
    yield mem
    mem.close()


def test_add_and_search_scoped(memory: Memory) -> None:
    memory.add(
        "User prefers dark mode and vim keybindings",
        user_id="alice",
        infer=False,
    )
    memory.add(
        "User likes hiking on weekends",
        user_id="bob",
        infer=False,
    )

    hits = memory.search(
        "editor preferences",
        filters={"user_id": "alice"},
        top_k=3,
    )["results"]

    assert hits
    assert hits[0]["memory"].lower().find("dark mode") >= 0


def test_delete_and_get(memory: Memory) -> None:
    created = memory.add("Timezone is US/Pacific", user_id="u1", infer=False)["results"]
    memory_id = created[0]["id"]

    fetched = memory.get(memory_id)
    assert fetched is not None
    assert fetched["memory"] == "Timezone is US/Pacific"

    memory.delete(memory_id)
    assert memory.get(memory_id) is None