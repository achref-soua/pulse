"""Agent graph mechanics — routing and the tool-execution loop, Groq faked.

Proves the graph actually calls a tool and loops back for a final answer, and
that the router steers direct questions past the tool machinery.
"""

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.ai.graph import _as_sources, _parse_route, build_graph


class FakeChat:
    """Minimal stand-in for ChatGroq: returns queued messages, ignores bind_tools."""

    def __init__(self, *replies):
        self._replies = list(replies)
        self._i = 0

    def bind_tools(self, _tools):
        return self

    async def ainvoke(self, _messages, **_kw):
        reply = self._replies[self._i]
        self._i += 1
        return reply


def test_parse_route():
    assert _parse_route("AGENT") == "agent"
    assert _parse_route("  direct \n") == "direct"
    assert _parse_route("") == "agent"  # safe default


def test_as_sources_parses_json_and_lists():
    assert _as_sources('[{"a": 1}]') == [{"a": 1}]
    assert _as_sources("not json") == []
    assert _as_sources([{"b": 2}]) == [{"b": 2}]


@pytest.mark.asyncio
async def test_agent_loop_executes_tool():
    tool_call = AIMessage(
        content="",
        tool_calls=[{
            "name": "calculate_risk_score",
            "args": {"kind": "rcri", "inputs": {
                "high_risk_surgery": True, "ischemic_heart_disease": True,
                "congestive_heart_failure": False, "cerebrovascular_disease": False,
                "insulin_dependent_diabetes": False, "preop_creatinine_gt_2": False,
            }},
            "id": "call_1", "type": "tool_call",
        }],
    )
    graph = build_graph(
        agent_model=FakeChat(tool_call, AIMessage(content="RCRI is 2 (class III).")),
        router_model=FakeChat(AIMessage(content="AGENT")),
    )
    state = await graph.ainvoke({
        "messages": [HumanMessage(content="What's this patient's RCRI?")],
        "patient_context": "", "route": "agent",
    })

    tool_msgs = [m for m in state["messages"] if isinstance(m, ToolMessage)]
    assert len(tool_msgs) == 1
    assert '"score": 2' in tool_msgs[0].content  # the real calculator ran
    assert state["messages"][-1].content == "RCRI is 2 (class III)."


@pytest.mark.asyncio
async def test_direct_route_skips_tools():
    graph = build_graph(
        agent_model=FakeChat(AIMessage(content="An aneurysm is a focal dilation.")),
        router_model=FakeChat(AIMessage(content="DIRECT")),
    )
    state = await graph.ainvoke({
        "messages": [HumanMessage(content="What is an aortic aneurysm?")],
        "patient_context": "", "route": "agent",
    })
    assert not [m for m in state["messages"] if isinstance(m, ToolMessage)]
    assert state["messages"][-1].content == "An aneurysm is a focal dilation."
