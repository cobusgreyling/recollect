from __future__ import annotations

import hashlib
import re

import numpy as np

from recollect.config import EmbedderConfig


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", text.lower())


class Embedder:
    def __init__(self, config: EmbedderConfig) -> None:
        self.config = config
        self._openai_client = None
        self._hf_model = None
        if config.provider == "openai":
            from openai import OpenAI

            self._openai_client = OpenAI(api_key=config.api_key, base_url=config.base_url)

    def embed(self, text: str) -> np.ndarray:
        provider = self.config.provider
        if provider == "local":
            return self._local_embed(text)
        if provider == "ollama":
            return self._ollama_embed(text)
        if provider == "huggingface":
            return self._hf_embed(text)
        assert self._openai_client is not None
        response = self._openai_client.embeddings.create(
            model=self.config.model,
            input=text,
            dimensions=self.config.dimensions,
        )
        vec = np.array(response.data[0].embedding, dtype=np.float32)
        return _normalize(vec)

    async def aembed(self, text: str) -> np.ndarray:
        import asyncio

        return await asyncio.to_thread(self.embed, text)

    def _local_embed(self, text: str) -> np.ndarray:
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

    def _ollama_embed(self, text: str) -> np.ndarray:
        import httpx

        base = (self.config.base_url or "http://127.0.0.1:11434").rstrip("/")
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{base}/api/embeddings",
                json={"model": self.config.model, "prompt": text},
            )
            response.raise_for_status()
            vec = np.array(response.json()["embedding"], dtype=np.float32)
        if vec.shape[0] != self.config.dimensions:
            vec = _resize(vec, self.config.dimensions)
        return _normalize(vec)

    def _hf_embed(self, text: str) -> np.ndarray:
        if self._hf_model is None:
            from sentence_transformers import SentenceTransformer

            self._hf_model = SentenceTransformer(self.config.model)
        vec = np.array(self._hf_model.encode(text), dtype=np.float32)
        if vec.shape[0] != self.config.dimensions:
            vec = _resize(vec, self.config.dimensions)
        return _normalize(vec)


def _resize(vec: np.ndarray, dims: int) -> np.ndarray:
    if vec.shape[0] == dims:
        return vec
    if vec.shape[0] > dims:
        return vec[:dims]
    out = np.zeros(dims, dtype=np.float32)
    out[: vec.shape[0]] = vec
    return out


def _normalize(vec: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(vec))
    if norm == 0.0:
        return vec
    return vec / norm


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b))