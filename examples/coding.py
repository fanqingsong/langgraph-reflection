"""Example of a LangGraph application with code reflection capabilities using Pyright.

Should install:

```
pip install langgraph-reflection langchain openevals pyright python-dotenv
```

To use Azure OpenAI:
1. Copy .env.example to .env and fill in your credentials
2. Or set the following environment variables:
   - AZURE_OPENAI_API_KEY: Your Azure OpenAI API key
   - AZURE_OPENAI_ENDPOINT: Your Azure OpenAI endpoint URL (e.g., https://your-resource.openai.azure.com/)
   - AZURE_OPENAI_API_VERSION: (Optional) API version, defaults to "2024-02-15-preview"

Or call setup_azure_openai() with the parameters before creating graphs.

To run with langgraph dev:
```bash
langgraph dev
```
"""

from langchain_core.messages import HumanMessage
from langgraph_reflection import create_reflection_graph

from examples.coding.assistant import create_assistant_graph
from examples.coding.judge import create_judge_graph
from examples.coding.config import setup_azure_openai


def create_graphs():
    """Create and configure the assistant and judge graphs."""
    # Create the assistant graph
    assistant_graph = create_assistant_graph()

    # Create the judge graph
    judge_graph = create_judge_graph()

    # Create the complete reflection graph
    return create_reflection_graph(assistant_graph, judge_graph).compile()


# Initialize Azure OpenAI if environment variables are set
# This allows the module to work if env vars are already configured
try:
    setup_azure_openai()
except ValueError:
    # Environment variables not set, user needs to call setup_azure_openai() before using
    pass


# Create the reflection app (will use Azure OpenAI if configured)
reflection_app = create_graphs()

if __name__ == "__main__":
    """Run an example query through the reflection system."""
    # Setup Azure OpenAI (if not already set via environment variables)
    # Uncomment and fill in your credentials if not using environment variables:
    # setup_azure_openai(
    #     api_key="your-azure-openai-api-key",
    #     endpoint="https://your-resource.openai.azure.com/",
    #     api_version="2024-02-15-preview"  # Optional
    # )
    
    example_query = [
        HumanMessage(content="Write a LangGraph RAG app")
    ]

    print("Running example with reflection...")
    result = reflection_app.invoke({"messages": example_query})
    print("Result:", result)
