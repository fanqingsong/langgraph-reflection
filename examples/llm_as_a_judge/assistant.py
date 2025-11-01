"""Assistant graph module for handling user queries and generating responses."""

from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, MessagesState, START, END


def call_model(state: dict) -> dict:
    """Process the user query with a large language model.

    Args:
        state: The current conversation state

    Returns:
        dict: Updated state with model response
    """
    model = init_chat_model(model="claude-3-7-sonnet-latest")
    return {"messages": model.invoke(state["messages"])}


def create_assistant_graph():
    """Create and configure the assistant graph.

    Returns:
        CompiledStateGraph: The compiled assistant graph
    """
    assistant_graph = (
        StateGraph(MessagesState)
        .add_node(call_model)
        .add_edge(START, "call_model")
        .add_edge("call_model", END)
        .compile()
    )
    return assistant_graph

