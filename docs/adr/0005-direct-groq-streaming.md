# ADR-0005: Direct `ChatGroq.astream()` for SSE chat

**Status:** Accepted  
**Date:** 2026-06-20

## Context

The AI Copilot needs token-by-token SSE streaming for the chat panel. Two approaches were considered:

1. Use LangGraph's `astream_events()` API on the full `StateGraph`, extracting `on_chat_model_stream` events.
2. Call `ChatGroq.astream()` directly in the FastAPI endpoint, bypassing LangGraph for the streaming path.

## Decision

Use `ChatGroq.astream()` directly (option 2) for the `/ai/chat` SSE endpoint. LangGraph's `StateGraph` is kept for the non-streaming patient-summary path (`run_summary()`), where state persistence and node composability matter.

## Rationale

- `astream_events()` emits many internal lifecycle events; filtering to just `on_chat_model_stream` requires non-obvious event-name matching and breaks on minor LangGraph version changes.
- The chat endpoint is inherently stateless between turns (history is sent in the request body); there is no need for LangGraph's checkpoint machinery here.
- Direct streaming is dramatically simpler: one `async for chunk in llm.astream(messages)` loop emitting `token` SSE events, with a `sources` event prepended and a `done` event appended.
- The split keeps the two paths independently testable: graph tests mock the Groq client; streaming tests assert SSE event shape without running the full graph.

## Consequences

- The chat panel does not benefit from LangGraph's routing or tool-use nodes — queries go straight to generation with a prepended system prompt and RAG context injected inline.
- If tool-use or multi-step routing is added to chat in future, the endpoint will need to migrate to `astream_events()` or a purpose-built streaming graph. This is an explicit known limitation, not an oversight.
