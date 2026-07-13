"""Tool-calling clinical agent on LangGraph.

    router ─► agent ⇄ tools        (agent loops through tools until it has an answer)
        └──► direct                (general knowledge → single completion)

The agent binds the grounded tools in ``app.ai.tools`` and never computes a
clinical score itself. An 8B router triages tool-worthy requests from general
questions so simple asks skip the tool machinery. Multi-turn memory is the
caller's job: pass the prior messages in (they come from the Conversation /
Message tables) — the graph itself is stateless per invocation.
"""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator

import structlog
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from app.ai.prompts import DIRECT_SYSTEM, SUMMARY_PROMPT, build_agent_system, format_sources
from app.ai.retriever import retrieve
from app.ai.state import PulseState
from app.ai.tools import TOOLS
from app.core.config import get_settings

log = structlog.get_logger()

_ROUTER_PROMPT = """You triage requests for a clinical decision-support assistant for aortic \
and endovascular surgery. Reply with exactly one word:
AGENT — if answering needs a patient record, a risk score, device/IFU matching, cohort counts, \
clinical notes, or a guideline/literature lookup.
DIRECT — if it is a general clinical-knowledge question needing no data lookup.

Request: {query}"""


def _parse_route(text: str) -> str:
    """Lenient parse of the router's one-word reply; default to the safe (agent) path."""
    return "direct" if "direct" in (text or "").strip().lower() else "agent"


def _last_human(messages: list[BaseMessage]) -> str:
    m = next((m for m in reversed(messages) if isinstance(m, HumanMessage)), None)
    return str(m.content) if m else ""


def build_graph(agent_model=None, router_model=None):
    """Compile the agent graph. Models are injectable so tests can pass fakes."""
    settings = get_settings()
    if agent_model is None:
        agent_model = ChatGroq(
            model=settings.groq_model,
            temperature=settings.groq_temperature,
            api_key=settings.groq_api_key,
            streaming=True,
        )
    if router_model is None:
        router_model = ChatGroq(
            model=settings.groq_router_model, temperature=0, api_key=settings.groq_api_key
        )
    agent_with_tools = agent_model.bind_tools(TOOLS)

    async def router_node(state: PulseState) -> dict:
        query = _last_human(state["messages"])
        try:
            reply = await router_model.ainvoke(
                [HumanMessage(content=_ROUTER_PROMPT.format(query=query))]
            )
            route = _parse_route(str(reply.content))
        except Exception as exc:  # router is a nicety — fall back to the full agent
            log.warning("router failed — defaulting to agent", error=str(exc))
            route = "agent"
        return {"route": route}

    async def agent_node(state: PulseState) -> dict:
        system = build_agent_system(state.get("patient_context", ""))
        reply = await agent_with_tools.ainvoke([SystemMessage(content=system), *state["messages"]])
        return {"messages": [reply]}

    async def direct_node(state: PulseState) -> dict:
        reply = await agent_model.ainvoke(
            [SystemMessage(content=DIRECT_SYSTEM), *state["messages"]]
        )
        return {"messages": [reply]}

    builder: StateGraph = StateGraph(PulseState)
    builder.add_node("router", router_node)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", ToolNode(TOOLS))
    builder.add_node("direct", direct_node)

    builder.add_edge(START, "router")
    builder.add_conditional_edges(
        "router", lambda s: s["route"], {"agent": "agent", "direct": "direct"}
    )
    builder.add_conditional_edges("agent", tools_condition)  # → "tools" | END
    builder.add_edge("tools", "agent")
    builder.add_edge("direct", END)
    return builder.compile()


_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


# ── streaming ─────────────────────────────────────────────────────────────
# Search tools whose output is worth surfacing to the UI as citable sources.
_SOURCE_TOOLS = {"search_guidelines", "search_device_catalog", "search_patient_notes"}


async def run_agent_events(
    messages: list[BaseMessage], patient_context: str = ""
) -> AsyncGenerator[dict, None]:
    """Drive the graph and yield normalized SSE events:
    router | tool_call | tool_result | sources | token | done.

    Tokens are emitted only from the answer nodes (agent/direct), never the router.
    """
    graph = get_graph()
    inputs = {"messages": messages, "patient_context": patient_context, "route": "agent"}
    final = ""
    async for ev in graph.astream_events(inputs, version="v2"):
        kind = ev["event"]
        node = ev.get("metadata", {}).get("langgraph_node")

        if kind == "on_chain_end" and node == "router":
            out = ev["data"].get("output")
            if isinstance(out, dict) and "route" in out:
                yield {"type": "router", "content": out["route"]}

        elif kind == "on_tool_start":
            yield {"type": "tool_call", "name": ev["name"], "args": ev["data"].get("input")}

        elif kind == "on_tool_end":
            output = ev["data"].get("output")
            payload = getattr(output, "content", output)  # ToolMessage → its content
            yield {"type": "tool_result", "name": ev["name"], "content": payload}
            if ev["name"] in _SOURCE_TOOLS:
                yield {"type": "sources", "name": ev["name"], "content": _as_sources(payload)}

        elif kind == "on_chat_model_stream" and node in ("agent", "direct"):
            chunk = ev["data"]["chunk"]
            if chunk.content:
                final += chunk.content
                yield {"type": "token", "content": chunk.content}

    yield {"type": "done", "content": final}


def _as_sources(payload) -> list:
    if isinstance(payload, str):
        try:
            return json.loads(payload)
        except (ValueError, TypeError):
            return []
    return payload if isinstance(payload, list) else []


# ── legacy non-streaming summary (used by report + patient-summary) ────────
async def run_summary(
    patient_data: str, query: str, scores_text: str = ""
) -> tuple[str, list[dict]]:
    """Non-streaming: retrieve guidelines then narrate a summary grounded in the
    pre-computed scores (which the model must quote, not recompute)."""
    settings = get_settings()
    docs = await retrieve(query, top_k=5)
    llm = ChatGroq(
        model=settings.groq_model,
        temperature=settings.groq_temperature,
        api_key=settings.groq_api_key,
    )
    prompt = SUMMARY_PROMPT.format(
        patient_data=patient_data,
        scores_section=scores_text or "No scores available.",
        sources_section=format_sources(docs),
    )
    response = await llm.ainvoke([SystemMessage(content=prompt)])
    return response.content, docs
