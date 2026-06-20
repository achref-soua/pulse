# ADR-0004: AGPL-3.0 license

**Status:** Accepted
**Date:** 2024-01-01

## Context

Pulse is an open-source portfolio project. We want users to be able to inspect, run, and fork it, but any derivative work (including SaaS deployments) must remain open-source.

## Decision

License under **GNU Affero General Public License v3 (AGPL-3.0)**, matching the license of Quiver (the bundled vector store).

## Consequences

- Any hosted deployment of Pulse must make its source available under AGPL-3.0.
- Consistent with the sibling projects (Quiver, Helio) which also use AGPL-3.0.
