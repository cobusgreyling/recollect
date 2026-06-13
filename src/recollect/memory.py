from __future__ import annotations

from typing import Any

from recollect.config import RecollectConfig
from recollect.memory_core import MemoryCore


class Memory(MemoryCore):
    """Synchronous long-term memory API for agents and assistants."""

    def __init__(self, config: RecollectConfig | None = None) -> None:
        super().__init__(config=config)