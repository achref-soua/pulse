# ADR-0009: The MCP server reuses the in-app agent's tool layer

**Status:** Accepted
**Date:** 2026-07-13

## Context

Pulse exposes an in-app clinical agent whose grounded tools live in `app/ai/tools.py` (score calculators, patient/device lookups, IFU device matching, guideline search, cohort queries). We also want external AI agents to drive Pulse's clinical capabilities over the Model Context Protocol (MCP). The risk of a second surface is drift: an MCP tool that computes or shapes results differently from the in-app tool would give two different answers for the same clinical question.

## Decision

The MCP server (`app/mcp/server.py`, FastMCP over stdio) is a thin adapter over the **same** `app/ai/tools.py` functions. Each MCP tool opens its own request-scoped DB session, binds it to the tool layer (`tools.bind_db`), and delegates to the existing tool. It adds no clinical logic of its own.

Exposed tools: `calculate_risk_score`, `score_patient`, `get_patient`, `match_devices`, `search_guidelines`, `query_cohort`.

## Rationale

- **One source of truth.** Scores still come from the tested calculators; device fit from the IFU engine; cohort facts from Postgres. An external agent gets byte-identical, grounded behaviour — it cannot invent a score any more than the in-app agent can.
- **No duplication.** The DB queries and grounding rules are written once. Fixing a tool fixes both surfaces.
- **Transport isolation.** MCP runs as a separate process over stdio, so it never shares the FastAPI request lifecycle; the per-call `AsyncSessionLocal` session keeps tenancy and lifecycle clean.

## Consequences

- The MCP server depends on the API package but is launched independently (`uv run python -m app.mcp`), not mounted on the HTTP app.
- `search_guidelines` needs the embedding model + Quiver; it degrades to an empty result when Quiver is unreachable, exactly as the in-app tool does.
- New agent tools are exposed to MCP by adding a one-line delegating wrapper — the temptation to fork logic is structurally removed.
