"""Quiver-backed retrieval with optional cross-encoder rerank."""

from __future__ import annotations

import asyncio
from functools import lru_cache

import structlog

from app.core.config import get_settings
from app.core.quiver_client import COLLECTION_GUIDELINES, COLLECTION_LITERATURE, get_quiver_client
from app.seed.generators import GUIDELINES_CORPUS, LITERATURE_CORPUS

log = structlog.get_logger()


@lru_cache(maxsize=1)
def _embedding_model():
    from sentence_transformers import SentenceTransformer  # lazy — heavy import
    return SentenceTransformer(get_settings().embedding_model)


@lru_cache(maxsize=1)
def _rerank_model():
    from sentence_transformers import CrossEncoder
    return CrossEncoder(get_settings().rerank_model)


def embed_sync(text: str) -> list[float]:
    return _embedding_model().encode(text, normalize_embeddings=True).tolist()


async def embed(text: str) -> list[float]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, embed_sync, text)


def _guideline_doc(hit_id: str, score: float) -> dict:
    try:
        idx = int(hit_id.rsplit("-", 1)[-1])
        g = GUIDELINES_CORPUS[idx]
        return {
            "id": hit_id,
            "type": "guideline",
            "title": g["title"],
            "section": g.get("section", ""),
            "body": g["body"],
            "source": g.get("source", "Synthetic guideline — educational only"),
            "score": score,
        }
    except (IndexError, ValueError):
        return {"id": hit_id, "type": "guideline", "title": "", "body": "", "source": "", "score": score}


def _literature_doc(hit_id: str, score: float) -> dict:
    try:
        idx = int(hit_id.rsplit("-", 1)[-1])
        g = LITERATURE_CORPUS[idx]
        return {
            "id": hit_id,
            "type": "literature",
            "title": g["title"],
            "section": g.get("section", ""),
            "body": g["body"],
            "source": g.get("source", "Synthetic literature — educational only"),
            "score": score,
        }
    except (IndexError, ValueError):
        return {"id": hit_id, "type": "literature", "title": "", "body": "", "source": "", "score": score}


def _rerank_sync(query: str, docs: list[dict], top_k: int) -> list[dict]:
    ce = _rerank_model()
    pairs = [(query, d["body"]) for d in docs]
    scores = ce.predict(pairs).tolist()
    ranked = sorted(zip(scores, docs, strict=False), key=lambda x: x[0], reverse=True)
    return [d for _, d in ranked[:top_k]]


async def retrieve(query: str, top_k: int = 5) -> list[dict]:
    """Embed query, dual-search Quiver, optionally rerank; returns ranked docs."""
    settings = get_settings()
    vec = await embed(query)

    try:
        async with get_quiver_client() as q:
            fetch_k = max(top_k, 4)
            guide_hits, lit_hits = await asyncio.gather(
                q.search(COLLECTION_GUIDELINES, vec, k=fetch_k),
                q.search(COLLECTION_LITERATURE, vec, k=fetch_k),
            )
    except Exception as exc:
        log.warning("quiver.search failed — returning empty sources", error=str(exc))
        return []

    docs: list[dict] = []
    for h in guide_hits:
        docs.append(_guideline_doc(h.id, h.score))
    for h in lit_hits:
        docs.append(_literature_doc(h.id, h.score))

    docs.sort(key=lambda d: d.get("score") or 0.0, reverse=True)

    if settings.rerank_enabled and len(docs) > top_k:
        try:
            loop = asyncio.get_event_loop()
            docs = await loop.run_in_executor(None, _rerank_sync, query, docs, top_k)
        except Exception as exc:
            log.warning("rerank failed — falling back to vector scores", error=str(exc))
            docs = docs[:top_k]
    else:
        docs = docs[:top_k]

    return docs


def all_knowledge() -> list[dict]:
    """Return all KB entries (no vectors) for the /ai/knowledge listing."""
    items: list[dict] = []
    for i, g in enumerate(GUIDELINES_CORPUS):
        items.append({
            "id": f"guideline-{i:03d}",
            "type": "guideline",
            "title": g["title"],
            "section": g.get("section", ""),
            "source": g.get("source", "Synthetic guideline — educational only"),
        })
    for i, g in enumerate(LITERATURE_CORPUS):
        items.append({
            "id": f"literature-{i:03d}",
            "type": "literature",
            "title": g["title"],
            "section": g.get("section", ""),
            "source": g.get("source", "Synthetic literature — educational only"),
        })
    return items
