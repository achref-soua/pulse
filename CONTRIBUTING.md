# Contributing to Pulse

## Branch naming

All work happens on short-lived branches off `develop`:

| Prefix       | Use                         |
|--------------|-----------------------------|
| `feature/`   | New features                |
| `fix/`       | Bug fixes                   |
| `chore/`     | Maintenance, deps, tooling  |
| `docs/`      | Documentation only          |
| `refactor/`  | Code restructuring          |
| `perf/`      | Performance improvements    |
| `test/`      | Test-only changes           |
| `ci/`        | CI/CD changes               |

`main` and `develop` are protected — no direct pushes; always open a PR.

## Commit messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(patients): add IFU-fit suitability engine

Support all six IFU envelope criteria (neck length, angulation, diameters,
iliac access, distal landing) and return per-criterion pass/fail verdicts.

Closes #42
```

Rules:
- Imperative subject line, lowercase after the scope
- Body explains *why*, not just *what*
- Reference issues with `Closes #N` or `Refs #N`

## Local gate — must pass before every merge

Run the full suite locally before opening a PR:

```bash
# Backend
cd apps/api
uv run ruff check .
uv run mypy app
uv run pytest -v --tb=short

# Frontend
pnpm turbo lint
pnpm turbo type-check
pnpm turbo test
```

CI workflows exist but are **manual only** (`workflow_dispatch`) — see below.

## Why CI is manual

Pulse's CI uses `on: workflow_dispatch` exclusively, with no automatic triggers
on push or pull request. This is intentional: it avoids consuming GitHub Actions
minutes on every commit and keeps the feedback loop in the developer's hands.
The local test gate above is the required merge gate. Trigger CI manually when
you want an independent verification of a branch before merging to `main`.

## Setup

```bash
# Prerequisites: Node ≥ 20.9, pnpm, Python 3.12, uv, Docker + Compose

git clone https://github.com/achref-soua/pulse.git
cd pulse
cp .env.example .env          # fill in GROQ_API_KEY for AI features

# Install dependencies
pnpm install
cd apps/api && uv sync && cd ../..

# Start the full stack
task up        # or: docker compose up -d --build --wait
task migrate
task seed
```

Open http://localhost:3000 and log in with the demo credentials in `.env.example`.

## Adding a new clinical calculator

1. Implement it as a pure function in `apps/api/app/clinical/`.
2. Add ≥3 unit tests in `apps/api/tests/clinical/` with the reference source
   cited in the docstring.
3. Document the reference in `docs/clinical/REFERENCES.md`.
4. Expose it as a FastAPI endpoint in `apps/api/app/api/routers/risk.py`.
5. Expose it as a LangGraph tool in `apps/api/app/ai/tools.py`.
6. Add a UI form in `apps/web/src/app/(app)/risk/`.
