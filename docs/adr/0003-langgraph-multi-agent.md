# ADR-0003: LangGraph stateful multi-agent graph

**Status:** Accepted
**Date:** 2024-01-01

## Context

The original project defined a LangGraph 2-node graph (retrieve → generate) but never wired it into the app. The orchestration ran through ad-hoc agent classes instead. We need a proper stateful multi-turn pipeline with routing, retrieval, tool use, generation, and guardrails.

## Decision

Implement a real `StateGraph` in `apps/api/app/ai/graph.py` with nodes: router → retrieve → tools → generate → guardrail. Persist conversation state via a Redis checkpointer keyed by `(user_id, conversation_id)`.

## Consequences

- Each node is a pure function on the graph state — easy to test in isolation by mocking the Groq client.
- The router node uses the fast `llama-3.1-8b-instant` model with structured Pydantic output + a deterministic regex fallback, preserving the original fallback behavior.
- Streaming is achieved by the generate node yielding SSE tokens; the FastAPI endpoint converts them to an EventSource stream.
- LangGraph checkpoints in Redis mean conversation history survives API restarts.
