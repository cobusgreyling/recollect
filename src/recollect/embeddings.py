from __future__ import annotations

import hashlib
import re

import numpy as np
from openai import OpenAI

from recollect.config import EmbedderConfig


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", text.lower())


class Embedder:
    def __init__(self, config: EmbedderConfig) -> None:
        self.config = config
        self._client: OpenAI | None = None
        if config.provider == "openai":
            self._client = OpenAI(api_key=config.api_key)

    def embed(self, text: str) -> np.ndarray:
        if self.config.provider == "local":
            return self._local_embed(text)
        assert self._client is not None
        response = self._client.embeddings.create(
            model=self.config.model,
            input=text,
            dimensions=self.config.dimensions,
        )
        vec = np.array(response.data[0].embedding, dtype=np.float32)
        return _normalize(vec)

    def _local_embed(self, text: str) -> np.ndarray:
        """Deterministic bag-of-hashes embedder for offline dev and tests."""
        dim = self.config.dimensions
        vec = np.zeros(dim, dtype=np.float32)
        for token in _tokenize(text):
            digest = hashlib.sha256(token.encode()).digest()
            for i in range(0, min(len(digest), dim), 4):
                idx = int.from_bytes(digest[i : i + 2], "big") % dim
                sign = 1.0 if digest[i + 2] % 2 == 0 else -1.0
                vec[idx] += sign
        if not _tokenize(text):
            vec[0] = 1.0
        return _normalize(vec)


def _normalize(vec: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(vec))
    if norm == 0.0:
        return vec
    return vec / norm


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b))