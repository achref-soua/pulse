# ADR-0002: Quiver as the vector store

**Status:** Accepted
**Date:** 2024-01-01

## Context

The original project used ChromaDB (local persistent client). We need a vector store for five knowledge-base collections: patients, devices, guidelines, literature, notes. Options considered: ChromaDB, pgvector, Qdrant, Quiver.

## Decision

Use **Quiver** — the owner's own from-scratch vector database (Rust, AGPL-3.0, at `../quiver`).

## Rationale

1. **Dogfooding**: the portfolio runs on its own infrastructure. README calls it out explicitly.
2. **Hybrid search**: Quiver supports vector + keyword search in one query, which is better for clinical text retrieval than pure ANN.
3. **Encryption-at-rest**: Quiver encrypts stored vectors and payloads, appropriate for a demo handling patient-like data.
4. **Integration**: official Python SDK (`quiver-client`) wraps the HTTP API cleanly; an `AsyncClient` is available for FastAPI async contexts.

## Consequences

- Quiver must be built from source (no published GHCR image); the docker-compose references the sibling `../quiver` context.
- The `QUIVER_URL` and `QUIVER_API_KEY` env vars are required at runtime.
- Collection schema (dim, metric) is decided at create time; changing it requires a drop-and-recreate.
