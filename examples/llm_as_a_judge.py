"""Example of LLM as a judge reflection system.

Should install:

```
pip install langgraph-reflection langchain openevals
```
"""

from langchain_core.messages import HumanMessage
from langgraph_reflection import create_reflection_graph

from examples.llm_as_a_judge.assistant import create_assistant_graph
from examples.llm_as_a_judge.judge import create_judge_graph


def create_graphs():
    """Create and configure the assistant and judge graphs."""
    # Create the assistant graph
    assistant_graph = create_assistant_graph()

    # Create the judge graph
    judge_graph = create_judge_graph()

    # Create the complete reflection graph
    return create_reflection_graph(assistant_graph, judge_graph).compile()


# Create the reflection app
reflection_app = create_graphs()


if __name__ == "__main__":
    """Run an example query through the reflection system."""
    example_query = [
        HumanMessage(
            content="Explain how nuclear fusion works and why it's important for clean energy"
        )
    ]

    print("Running example with reflection...")
    result = reflection_app.invoke({"messages": example_query})
    print("Result:", result)
