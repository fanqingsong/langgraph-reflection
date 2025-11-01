"""Judge graph module for code extraction, validation, and reflection."""

from typing import TypedDict

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, MessagesState, START, END

# openevals 是一个开源评测与自动化代码测试框架，常用于自动评估 AI 生成代码的正确性及功能表现。
# 它支持多种编程语言和评测方式，尤其适合集成到大模型代码能力测试或RAG应用中。
# 例如 openevals.code.pyright.create_pyright_evaluator 用于调用 pyright 静态类型检查器自动分析/验证 python 代码的类型问题和潜在错误。
from openevals.code.pyright import create_pyright_evaluator

from .config import get_azure_model_name


# Define type classes for code extraction
class ExtractPythonCode(TypedDict):
    """Type class for extracting Python code. The python_code field is the code to be extracted."""

    python_code: str


class NoCode(TypedDict):
    """Type class for indicating no code was found."""

    no_code: bool


# System prompt for the model
SYSTEM_PROMPT = """The below conversation is you conversing with a user to write some python code. Your final response is the last message in the list.

Sometimes you will respond with code, othertimes with a question.

If there is code - extract it into a single python script using ExtractPythonCode.

If there is no code to extract - call NoCode."""


def try_running(state: dict) -> dict | None:
    """Attempt to run and analyze the extracted Python code.

    Args:
        state: The current conversation state

    Returns:
        dict | None: Updated state with analysis results if code was found
    """
    model = init_chat_model(
        model=get_azure_model_name("gpt-4o-mini"),
        model_provider="azure_openai"
    )

    extraction = model.bind_tools([ExtractPythonCode, NoCode])

    er = extraction.invoke(
        [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    )

    # Check if code was extracted
    if len(er.tool_calls) == 0:
        # No tool calls means model didn't find extractable code or didn't use tools
        # This is normal when the response is just a question or explanation
        # Return None to continue without feedback (validation passed)
        print("⚠️ No code extracted - model response may not contain extractable code")
        return None
        
    tc = er.tool_calls[0]
    if tc["name"] != "ExtractPythonCode":
        # NoCode was called or other tool - no code to validate
        # Return None to continue without feedback (validation passed)
        print(f"⚠️ Tool call was '{tc['name']}', not ExtractPythonCode - no code to validate")
        return None
    
    print(f"✅ Extracted code (length: {len(tc['args']['python_code'])} chars)")

    # Extract code and run pyright validation
    extracted_code = tc["args"]["python_code"]
    evaluator = create_pyright_evaluator()
    result = evaluator(outputs=extracted_code)
    print(f"Pyright evaluation result: {result}")

    # Handle pyright evaluation result
    if not result["score"]:
        # Code has errors - provide feedback to assistant
        comment = result.get("comment", "Unknown error")
        # If comment is just "Failed to parse Pyright output", provide more context
        if comment == "Failed to parse Pyright output: " or comment.startswith("Failed to parse Pyright output"):
            return {
                "messages": [
                    HumanMessage(
                        content="I tried to validate the code with Pyright, but encountered an issue. "
                        "Please review the code for syntax errors, type issues, and best practices. "
                        "Make sure the code is complete and can be executed as a standalone script."
                    )
                ]
            }
        else:
            return {
                "messages": [
                    HumanMessage(
                        content=f"I ran pyright and found this: {comment}\n\n"
                        "Try to fix it. Make sure to regenerate the entire code snippet. "
                        "If you are not sure what is wrong, or think there is a mistake, "
                        "you can ask me a question rather than generating code"
                    )
                ]
            }
    
    # Code passed validation (score is True)
    # Return None to indicate success - no feedback needed, process will end
    print("✅ Code passed Pyright validation")
    return None


def create_judge_graph():
    """Create and configure the judge graph for code analysis.

    Returns:
        CompiledStateGraph: The compiled judge graph
    """
    judge_graph = (
        StateGraph(MessagesState)
        .add_node(try_running)
        .add_edge(START, "try_running")
        .add_edge("try_running", END)
        .compile()
    )
    return judge_graph

