# ADR-0010: A tool-calling agent graph replaces single-shot RAG

**Status:** Accepted
**Date:** 2026-07-13

## Context

The first AI implementation was single-shot RAG: embed the question, search Quiver, stuff the passages into one prompt, and return one completion. A compiled `retrieve → generate` LangGraph existed but was never invoked. This shape cannot reason over multiple steps, cannot call the clinical calculators, and — most importantly — leaves the model free to *state* a score it never *computed*.

## Decision

Replace it with a real tool-calling agent on LangGraph:

```
router ─► agent ⇄ tools      (loop through ToolNode via tools_condition until answered)
    └──► direct              (general knowledge → one completion, no tools)
```

- A fast **router** model (8B) triages tool-worthy requests from general questions.
- The **agent** (70B) binds eight grounded tools (`app/ai/tools.py`) and loops through a `ToolNode` until it produces a final answer.
- Grounding is enforced by the system prompt *and* structurally: `score_patient` derives calculator inputs from the chart, so the model cannot supply invented inputs.
- Multi-turn memory is the persisted `Conversation`/`Message` history, replayed into the graph — the graph itself stays stateless.
- The graph is streamed via `astream_events`, normalized into SSE events (`router`, `tool_call`, `tool_result`, `sources`, `token`, `done`).

## Rationale

- **Grounding.** The agent orchestrates; the deterministic engine computes. A clinical claim traces to a tool result or a cited guideline.
- **Reasoning.** Multi-step questions ("score this patient *and* check EVAR suitability") need more than one retrieval and one completion.
- **Transparency.** Streaming the tool steps makes the reasoning visible — the copilot renders a live agent timeline rather than an opaque paragraph.
- **Testability.** Models are injectable (`build_graph(agent_model=, router_model=)`), so the tool-execution loop is unit-tested with no live LLM.

## Consequences

- Two model tiers are configured (`groq_model`, `groq_router_model`); the router adds one cheap call per turn.
- No graph-level checkpointer is used — memory is the app's own tables, avoiding a second store to keep in sync.
- New capabilities are added by writing a grounded tool, not by expanding a prompt.
