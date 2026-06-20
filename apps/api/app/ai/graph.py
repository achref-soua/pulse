"""LangGraph patient-summary workflow (retrieve → generate)."""

from __future__ import annotations

import structlog
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph

from app.ai.prompts import SUMMARY_PROMPT, format_sources
from app.ai.retriever import retrieve
from app.ai.state import PulseState
from app.core.config import get_settings

log = structlog.get_logger()


async def _retrieve_node(state: PulseState) -> dict:
    last = next((m for m in reversed(state["messages"]) if isinstance(m, HumanMessage)), None)
    query = last.content if last else ""
    if not query:
        return {"sources": []}
    docs = await retrieve(query, top_k=5)
    return {"sources": docs}


async def _generate_node(state: PulseState) -> dict:
    from app.ai.prompts import build_system_prompt

    settings = get_settings()
    llm = ChatGroq(
        model=settings.groq_model,
        temperature=settings.groq_temperature,
        api_key=settings.groq_api_key,
    )
    system = build_system_prompt(state.get("patient_context", ""), state.get("sources", []))
    messages = [SystemMessage(content=system), *state["messages"]]
    response = await llm.ainvoke(messages)
    return {"messages": [response]}


def build_graph() -> object:
    builder: StateGraph = StateGraph(PulseState)
    builder.add_node("retrieve", _retrieve_node)
    builder.add_node("generate", _generate_node)
    builder.set_entry_point("retrieve")
    builder.add_edge("retrieve", "generate")
    builder.add_edge("generate", END)
    return builder.compile()


# Module-level singleton — created once per process
_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


async def run_summary(patient_data: str, query: str) -> tuple[str, list[dict]]:
    """Non-streaming: retrieve relevant guidelines then generate a patient summary."""
    settings = get_settings()
    docs = await retrieve(query, top_k=5)
    llm = ChatGroq(
        model=settings.groq_model,
        temperature=settings.groq_temperature,
        api_key=settings.groq_api_key,
    )
    prompt = SUMMARY_PROMPT.format(patient_data=patient_data, sources_section=format_sources(docs))
    response = await llm.ainvoke([SystemMessage(content=prompt)])
    return response.content, docs
