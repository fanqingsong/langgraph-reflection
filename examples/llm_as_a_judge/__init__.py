"""LLM as a judge example module with assistant and judge subgraphs."""

from .assistant import create_assistant_graph
from .judge import create_judge_graph

__all__ = ["create_assistant_graph", "create_judge_graph"]

