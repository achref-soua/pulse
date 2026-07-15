# Changelog

All notable changes to Pulse are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Pulse uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] — 2026-07-14

The premium + agentic transformation: grounded tool-calling AI, a Clinical Cobalt
design system in light and dark, and a full feature round-out.

### Added
- **Agentic AI copilot** — a tool-calling LangGraph agent (router → agent ⇄ tools) replacing single-shot RAG; eight grounded tools over the clinical engine, Quiver, and the cohort; streamed reasoning (`router`/`tool_call`/`tool_result`/`sources`/`token`); multi-turn memory via `Conversation`/`Message`; a redesigned copilot with an agent-step timeline and a full-page `/copilot`
- **`score_patient`** tool deriving calculator inputs from the chart so scores are grounded end-to-end
- **Grounded report** — `/ai/patient-summary` and `/ai/report` compute every applicable score deterministically and narrate around them
- **MCP server** (`app/mcp`) exposing the clinical tools to external agents over stdio, reusing the in-app tool layer
- **Clinical Cobalt design system** — token-based light/dark theming, `@pulse/ui` Radix primitives, tokenized pages and charts
- **Public landing page**, **⌘K command palette**, **`/analytics` cohort dashboard**, and **NL→cohort** roster search (schema-validated, fail-closed)
- **EuroSCORE II** calculator (now 7 calculators)
- **"Pulse, Explained"** designed field-guide PDF (`docs/pulse-explained.pdf`)
- ADRs 0009–0012 (MCP tool-sharing, agent graph, design tokens, NL-cohort)

### Changed
- Quiver client upgraded to the published `quiver-client` 0.35.0
- Copilot, dashboard, and every page rebuilt on design tokens; screenshots regenerated in light + dark

### Fixed
- `/dashboard/stats` and `/users` listing (UUID/window-function bugs)
- `/devices` listing 500 (UUID response-model type)
- `query_cohort` tool hard-failing when the model omitted `filters`
- NL→cohort fail-open that could return the whole cohort on a failed extraction

## [1.0.0]

### Added
- Initial monorepo foundation (Turborepo + pnpm + uv)
- FastAPI backend with SQLAlchemy 2.0 + Alembic migrations
- Next.js 15 frontend with Tailwind + shadcn/ui
- Quiver vector database integration for the knowledge base
- PostgreSQL data model: users, patients, comorbidities, labs, medications, vitals, devices, clinical notes, conversations, risk assessments, audit log
- JWT authentication (access + refresh) with RBAC (surgeon / anesthetist / nurse / admin)
- Docker Compose stack: web, api, db, quiver, redis
- Manual GitHub Actions CI workflows (lint, type-check, test, security scan, release)
- AGPL-3.0 license

[2.0.0]: https://github.com/achref-soua/pulse/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/achref-soua/pulse/releases/tag/v1.0.0
