from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    provider: Literal["openai"] = "openai"
    model: str = "gpt-4o-mini"
    api_key: str | None = None
    base_url: str | None = None


class EmbedderConfig(BaseModel):
    provider: Literal["openai", "local"] = "openai"
    model: str = "text-embedding-3-small"
    api_key: str | None = None
    dimensions: int = 256


class RecollectConfig(BaseModel):
    data_dir: Path = Field(default_factory=lambda: Path.home() / ".recollect")
    llm: LLMConfig = Field(default_factory=LLMConfig)
    embedder: EmbedderConfig = Field(default_factory=EmbedderConfig)
    extraction_enabled: bool = True
    hybrid_keyword_weight: float = 0.35
    entity_boost: float = 0.15
    default_top_k: int = 5