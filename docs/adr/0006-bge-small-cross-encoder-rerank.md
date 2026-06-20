# ADR-0006: `bge-small-en-v1.5` embeddings + cross-encoder reranking

**Status:** Accepted  
**Date:** 2026-06-20

## Context

The RAG pipeline needs an embedding model to vectorise queries and knowledge-base documents at seed time, and optionally a reranker to improve candidate ordering before generation.

Options considered for embeddings:
- `text-embedding-ada-002` / `text-embedding-3-small` (OpenAI) — requires API key, latency, cost
- `all-MiniLM-L-6-v2` — fast, widely used, but lower retrieval quality on technical text
- `BAAI/bge-small-en-v1.5` — state-of-the-art on MTEB for its size, fully local, MIT licence
- `BAAI/bge-large-en-v1.5` — better quality but 5× larger; excess for a 13-entry knowledge base

Options for reranking:
- No reranking — simpler, but top-k by cosine alone misses relevance signal
- `cross-encoder/ms-marco-MiniLM-L-6-v2` — standard BEIR reranker, local, fast on CPU

## Decision

- Embeddings: `BAAI/bge-small-en-v1.5` (33 M parameters, 384 dimensions)
- Reranker: `cross-encoder/ms-marco-MiniLM-L-6-v2`, toggled via `RERANK_ENABLED=true`
- Both run locally via `sentence-transformers`; no external embedding API

## Rationale

- Local models eliminate per-query cost and API dependency for a demo that may run offline
- `bge-small-en-v1.5` ranks near `text-embedding-ada-002` on MTEB retrieval benchmarks at a fraction of the size
- Cross-encoder reranking consistently improves precision@k in RAG pipelines; the overhead is negligible for k ≤ 20 candidates on a 13-entry knowledge base
- `RERANK_ENABLED` env flag allows disabling reranking on resource-constrained hosts

## Consequences

- Seed time includes a one-off model download (~130 MB for embeddings, ~67 MB for reranker); subsequent runs use the local cache
- Embedding dimensions (384) must match the Quiver collection schema; changing the model requires a full reseed
