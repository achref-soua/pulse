from typing import Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class PulseState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    patient_context: str  # pre-formatted patient summary injected into system prompt
    sources: list[dict]   # retrieved docs forwarded to the client
