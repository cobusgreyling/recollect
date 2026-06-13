from __future__ import annotations

import math
from collections import Counter

import numpy as np

from recollect.config import RecollectConfig
from recollect.embeddings import cosine_similarity
from recollect.types import MemoryRecord, SearchHit


def _tokenize(text: str) -> list[str]:
    return [t for t in text.lower().split() if t]


def bm25_score(query_tokens: list[str], doc_tokens: list[str], avg_dl: float, k1: float = 1.5, b: float = 0.75) -> float:
    if not query_tokens or not doc_tokens:
        return 0.0
    dl = len(doc_tokens)
    tf = Counter(doc_tokens)
    score = 0.0
    for term in query_tokens:
        if term not in tf:
            continue
        freq = tf[term]
        idf = math.log(1 + 1)  # single-doc corpus per query batch; refined with global stats later
        denom = freq + k1 * (1 - b + b * dl / max(avg_dl, 1.0))
        score += idf * (freq * (k1 + 1)) / denom
    return score


def hybrid_search(
    *,
    query: str,
    query_embedding: np.ndarray,
    candidates: list[tuple[MemoryRecord, np.ndarray]],
    config: RecollectConfig,
    top_k: int,
) -> list[SearchHit]:
    if not candidates:
        return []

    query_tokens = _tokenize(query)
    doc_token_lists = [_tokenize(rec.text) for rec, _ in candidates]
    avg_dl = sum(len(d) for d in doc_token_lists) / max(len(doc_token_lists), 1)

    bm25_scores = [
        bm25_score(query_tokens, doc_tokens, avg_dl) for doc_tokens in doc_token_lists
    ]
    max_bm25 = max(bm25_scores) if bm25_scores else 0.0

    query_entities = {t.lower() for t in query.split() if t[:1].isupper()}

    hits: list[SearchHit] = []
    for (record, emb), raw_bm25 in zip(candidates, bm25_scores):
        semantic = cosine_similarity(query_embedding, emb)
        keyword = (raw_bm25 / max_bm25) if max_bm25 > 0 else 0.0
        entity_overlap = 0.0
        if record.entities:
            ent_set = {e.lower() for e in record.entities}
            overlap = len(query_entities & ent_set)
            entity_overlap = overlap / max(len(ent_set), 1)

        fused = (
            (1.0 - config.hybrid_keyword_weight) * semantic
            + config.hybrid_keyword_weight * keyword
            + config.entity_boost * entity_overlap
        )
        hits.append(
            SearchHit(
                id=record.id,
                memory=record.text,
                score=fused,
                created_at=record.created_at,
                metadata={
                    "semantic": semantic,
                    "keyword": keyword,
                    "entity_overlap": entity_overlap,
                    **record.scope.metadata,
                },
            )
        )

    hits.sort(key=lambda h: h.score, reverse=True)
    return hits[:top_k]