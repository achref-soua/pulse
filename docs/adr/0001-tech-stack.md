# ADR-0001: Tech stack selection

**Status:** Accepted
**Date:** 2024-01-01

## Context

Rebuilding a Streamlit chat prototype into a full clinical decision-support demo. Need a stack that is modern, fast, type-safe, and portfolio-quality.

## Decision

- **Frontend:** Next.js 15 (App Router) + TypeScript + Tailwind + shadcn/ui
- **Backend:** FastAPI (Python 3.12, uv) + SQLAlchemy 2.0 async + Alembic
- **Vector store:** Quiver (see ADR-0002)
- **LLM orchestration:** LangGraph + langchain-groq
- **Relational DB:** PostgreSQL 16
- **Cache / checkpoints:** Redis
- **Monorepo:** Turborepo + pnpm workspaces + uv

## Consequences

- FastAPI's automatic OpenAPI generation lets us derive TypeScript client types via `openapi-typescript`, eliminating an entire class of frontend/backend drift bugs.
- SQLAlchemy 2.0 async + Alembic gives production-grade schema management with a clear migration history.
- Turborepo caches and parallelises lint/test/build across the monorepo.
- uv replaces pip/poetry for Python dependency management: deterministic lockfile, fast installs.
