# Changelog

All notable changes to Pulse are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Pulse uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/achref-soua/pulse/compare/HEAD...HEAD
