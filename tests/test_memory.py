from __future__ import annotations

from pathlib import Path

import pytest

from recollect.config import RecollectConfig
from recollect.memory import Memory


@pytest.fixture(params=["local_dev", "in_memory"])
def memory(request, tmp_path: Path) -> Memory:
    if request.param == "in_memory":
        config = RecollectConfig.in_memory()
    else:
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


def test_get_all_and_filters(memory: Memory) -> None:
    memory.add("Fact A for alice", user_id="alice", infer=False)
    memory.add("Fact B for alice run1", user_id="alice", run_id="run1", infer=False)
    memory.add("Fact C for bob", user_id="bob", infer=False)

    all_res = memory.get_all()
    assert len(all_res["results"]) == 3

    alice = memory.get_all(filters={"user_id": "alice"})
    assert len(alice["results"]) == 2

    alice_run = memory.get_all(filters={"user_id": "alice", "run_id": "run1"})
    assert len(alice_run["results"]) == 1
    assert "run1" in str(alice_run)


def test_delete_nonexistent_returns_not_found(memory: Memory) -> None:
    res = memory.delete("does-not-exist-123")
    assert res["message"] == "not_found"


def test_add_with_infer_false_raw_strings(memory: Memory) -> None:
    res = memory.add("Just a raw preference note", user_id="u9", infer=False)
    assert len(res["results"]) == 1
    assert "preference note" in res["results"][0]["memory"]


def test_search_top_k_and_empty(memory: Memory) -> None:
    memory.add("Some fact about Python", user_id="pyuser", infer=False)
    res = memory.search("python", filters={"user_id": "pyuser"}, top_k=10)
    assert len(res["results"]) >= 1

    empty = memory.search("completely unknown query xyz", filters={"user_id": "pyuser"}, top_k=5)
    # May return low scoring or zero; just ensure no crash and list
    assert isinstance(empty["results"], list)
