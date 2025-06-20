from langgraph.graph.message import add_messages
from typing import Annotated, TypedDict, Any
from langchain_core.messages import AnyMessage

class State(TypedDict):
    query: str
    user_id: str