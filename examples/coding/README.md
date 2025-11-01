# Coding Example with LangGraph Dev

This example demonstrates a LangGraph application with code reflection capabilities using Azure OpenAI and Pyright.

## Setup

1. **Install dependencies:**
   ```bash
   pip install langgraph-reflection langchain openevals pyright python-dotenv
   pip install -U "langgraph-cli[inmem]"
   ```

2. **Configure Azure OpenAI:**
   ```bash
   # Copy the example env file
   cp .env.example .env
   
   # Edit .env and fill in your Azure OpenAI credentials
   # AZURE_OPENAI_API_KEY=your-key
   # AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   # AZURE_OPENAI_API_VERSION=2024-02-15-preview
   ```

3. **Start the LangGraph dev server:**
   ```bash
   # From project root
   langgraph dev
   ```

   This will start the dev server at `http://localhost:2024`

## Usage

After starting `langgraph dev`, you can:
- Access the API at `http://localhost:2024`
- View API docs at `http://localhost:2024/docs`
- Use LangGraph Studio at `https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024`

## Manual Execution

You can also run the example directly:
```bash
python examples/coding.py
```

## Configuration

The application automatically loads environment variables from `.env` file when available.
You can also set environment variables directly, or call `setup_azure_openai()` in code.

