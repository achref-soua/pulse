# ADR-0012: Natural-language cohort search is schema-validated and fails closed

**Status:** Accepted
**Date:** 2026-07-13

## Context

The patient roster supports a plain-English search — "post-op patients with large aneurysms over 75". A language model turns that sentence into structured filters. Two risks come with letting a model shape a database query: it can emit a key the query layer does not expect (or a malicious one), and it can fail to extract anything at all — and a query built from *no* filters matches *everything*.

## Decision

- **Validate through a schema.** The model returns JSON; it is coerced through a Pydantic `CohortFilters` model before any of it reaches the query. A key the schema does not define cannot influence the result — only the known filter fields (phase, intervention, aneurysm type, sex, min diameter, age range) are honoured.
- **Reuse the roster.** `GET /patients` is extended to honour those same filters, so natural-language results flow through the existing paginated, role-gated roster rather than a parallel query path.
- **Fail closed.** If extraction errors or maps to no filters, the endpoint returns an empty result — never an unconstrained query that would dump the entire cohort.

## Rationale

- **Injection safety.** The model's free-text output never becomes query structure directly; the schema is the boundary.
- **No silent widening.** A failed extraction that returns every patient is worse than returning none — the user believes a filter applied. Failing closed makes the failure visible.
- **One query path.** Extending `/patients` avoids a second, divergent way to list patients.

## Consequences

- The fast 8B router model is reused for extraction (`response_format: json_object`), keeping the call cheap.
- A query that legitimately maps to no filters returns nothing; "show me everyone" is the roster's job, not the NL search's.
- Adding a new filter means adding it to both `CohortFilters` and the `/patients` query — a deliberate, reviewable pair.
