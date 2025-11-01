"""Judge graph module for evaluating assistant responses using LLM as a judge."""

from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from openevals.llm import create_llm_as_judge


# Define a more detailed critique prompt with specific evaluation criteria
CRITIQUE_PROMPT = """You are an expert judge evaluating AI responses. Your task is to critique the AI assistant's latest response in the conversation below.

Evaluate the response based on these criteria:
1. Accuracy - Is the information correct and factual?
2. Completeness - Does it fully address the user's query?
3. Clarity - Is the explanation clear and well-structured?
4. Helpfulness - Does it provide actionable and useful information?
5. Safety - Does it avoid harmful or inappropriate content?

If the response meets ALL criteria satisfactorily, set pass to True.

If you find ANY issues with the response, do NOT set pass to True. Instead, provide specific and constructive feedback in the comment key and set pass to False.

Be detailed in your critique so the assistant can understand exactly how to improve.

<response>
{outputs}
</response>"""


def judge_response(state: dict, config: dict | None = None) -> dict | None:
    """Evaluate the assistant's response using a separate judge model.

    Args:
        state: The current conversation state
        config: Optional configuration dictionary

    Returns:
        dict | None: Updated state with critique if improvements are needed, None otherwise
    """
    evaluator = create_llm_as_judge(
        prompt=CRITIQUE_PROMPT,
        model="openai:o3-mini",
        feedback_key="pass",
    )
    eval_result = evaluator(outputs=state["messages"][-1].content, inputs=None)

    if eval_result["score"]:
        print("✅ Response approved by judge")
        return None
    else:
        # Otherwise, return the judge's critique as a new user message
        print("⚠️ Judge requested improvements")
        return {"messages": [HumanMessage(content=eval_result["comment"])]}


def create_judge_graph():
    """Create and configure the judge graph for response evaluation.

    Returns:
        CompiledStateGraph: The compiled judge graph
    """
    judge_graph = (
        StateGraph(MessagesState)
        .add_node(judge_response)
        .add_edge(START, "judge_response")
        .add_edge("judge_response", END)
        .compile()
    )
    return judge_graph

