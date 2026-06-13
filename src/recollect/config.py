from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    provider: Literal["openai"] = "openai"
    model: str = "gpt-4o-mini"
    api_key: str | None = Field(default_factory=lambda: os.environ.get("OPENAI_API_KEY"))
    base_url: str | None = None


class EmbedderConfig(BaseModel):
    provider: Literal["openai", "local", "ollama", "huggingface"] = "openai"
    model: str = "text-embedding-3-small"
    api_key: str | None = Field(default_factory=lambda: os.environ.get("OPENAI_API_KEY"))
    base_url: str | None = None
    dimensions: int = 256


class VectorStoreConfig(BaseModel):
    provider: Literal["sqlite", "memory", "qdrant", "chroma", "pgvector"] = "sqlite"
    sqlite_path: Path | None = None
    chroma_path: str | None = None
    collection_name: str = "recollect"
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    pg_dsn: str | None = None
    embedding_dims: int = 256


class RecollectConfig(BaseModel):
    data_dir: Path = Field(default_factory=lambda: Path.home() / ".recollect")
    llm: LLMConfig = Field(default_factory=LLMConfig)
    embedder: EmbedderConfig = Field(default_factory=EmbedderConfig)
    vector_store: VectorStoreConfig = Field(default_factory=VectorStoreConfig)
    extraction_enabled: bool = True
    hybrid_keyword_weight: float = 0.35
    entity_boost: float = 0.15
    default_top_k: int = 5

    @classmethod
    def local_dev(cls) -> RecollectConfig:
        """No API keys: local embedder, SQLite, raw message ingest."""
        return cls(
            extraction_enabled=False,
            embedder=EmbedderConfig(provider="local", dimensions=64),
            vector_store=VectorStoreConfig(provider="sqlite", embedding_dims=64),
        )

    @classmethod
    def in_memory(cls) -> RecollectConfig:
        """Fast, ephemeral in-memory store + local embedder. Ideal for unit tests and benchmarks."""
        return cls(
            extraction_enabled=False,
            embedder=EmbedderConfig(provider="local", dimensions=64),
            vector_store=VectorStoreConfig(provider="memory", embedding_dims=64),
        )
