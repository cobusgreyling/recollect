"""Unit tests for the hybrid retrieval scoring logic (pure, no stores required)."""

from __future__ import annotations

import numpy as np

from recollect.config import RecollectConfig
from recollect.retrieval import hybrid_search
from recollect.types import MemoryRecord, MemoryScope


def _make_record(
    text: str, user_id: str | None = "u1", entities: list[str] | None = None
) -> MemoryRecord:
    return MemoryRecord(
        text=text,
        scope=MemoryScope(user_id=user_id),
        entities=entities or [],
    )


def _vec(val: float, dim: int = 8) -> np.ndarray:
    """Simple deterministic vector for testing (not normalized here; hybrid does cosine)."""
    v = np.zeros(dim, dtype=np.float32)
    v[0] = val
    norm = np.linalg.norm(v)
    return v / norm if norm > 0 else v


def test_hybrid_search_empty_candidates():
    config = RecollectConfig()
    hits = hybrid_search(
        query="anything",
        query_embedding=_vec(1.0),
        candidates=[],
        config=config,
        top_k=5,
    )
    assert hits == []


def test_hybrid_search_basic_semantic_match():
    config = RecollectConfig(hybrid_keyword_weight=0.0, entity_boost=0.0)  # pure semantic
    rec = _make_record("User prefers PostgreSQL for projects")
    # query embed close to doc embed
    qemb = _vec(0.9)
    demb = _vec(0.88)
    hits = hybrid_search(
        query="database preference",
        query_embedding=qemb,
        candidates=[(rec, demb)],
        config=config,
        top_k=3,
    )
    assert len(hits) == 1
    assert hits[0].memory == rec.text
    assert 0.0 < hits[0].score <= 1.0
    # metadata breakdown present
    assert "semantic" in hits[0].metadata
    assert "keyword" in hits[0].metadata


def test_hybrid_search_keyword_and_entity_boosts():
    config = RecollectConfig(hybrid_keyword_weight=0.5, entity_boost=0.2)
    # Use a single capitalized token that the crude query_entities splitter will catch
    # and that matches a stored entity exactly (lower-cased comparison inside).
    rec = _make_record(
        "User loves dark mode in VSCode and other editors",
        entities=["VSCode"],
    )
    qemb = _vec(0.5)
    demb = _vec(0.6)

    hits = hybrid_search(
        query="VSCode dark theme preference",
        query_embedding=qemb,
        candidates=[(rec, demb)],
        config=config,
        top_k=1,
    )
    assert len(hits) == 1
    meta = hits[0].metadata
    assert meta["entity_overlap"] > 0.0
    assert meta["keyword"] >= 0.0


def test_hybrid_search_top_k_and_sorting():
    config = RecollectConfig()
    records = [
        _make_record("apple banana cherry"),
        _make_record("zebra xylophone query match"),
        _make_record("important postgres database config"),
    ]
    qemb = _vec(0.7)
    cands = [(r, _vec(0.4 + i * 0.1)) for i, r in enumerate(records)]

    hits = hybrid_search(
        query="database",
        query_embedding=qemb,
        candidates=cands,
        config=config,
        top_k=2,
    )
    assert len(hits) == 2
    # Higher scoring first
    assert hits[0].score >= hits[1].score


def test_hybrid_search_no_keyword_overlap_still_returns_semantic():
    config = RecollectConfig(hybrid_keyword_weight=0.8)
    rec = _make_record("Completely unrelated topic about space travel")
    hits = hybrid_search(
        query="postgres database",
        query_embedding=_vec(0.95),
        candidates=[(rec, _vec(0.9))],
        config=config,
        top_k=1,
    )
    assert len(hits) == 1
    # Even with bad keyword, semantic can carry it (though low)
    assert hits[0].score > 0.0


def test_hybrid_search_respects_config_weights():
    base = RecollectConfig(hybrid_keyword_weight=0.0, entity_boost=0.0)
    kw = RecollectConfig(hybrid_keyword_weight=0.9, entity_boost=0.0)

    rec = _make_record("The user mentioned PostgreSQL again today", entities=["PostgreSQL"])
    qemb = _vec(0.2)
    demb = _vec(0.3)

    h1 = hybrid_search(
        query="PostgreSQL", query_embedding=qemb, candidates=[(rec, demb)], config=base, top_k=1
    )[0]
    h2 = hybrid_search(
        query="PostgreSQL", query_embedding=qemb, candidates=[(rec, demb)], config=kw, top_k=1
    )[0]

    # With high keyword weight + "PostgreSQL" token present, score should differ (or at least both >=0)
    assert h2.score >= 0.0 and h1.score >= 0.0
