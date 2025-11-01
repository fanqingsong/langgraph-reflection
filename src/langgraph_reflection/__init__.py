from typing import Optional, Type, Any, Literal, get_type_hints
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.graph.state import CompiledStateGraph
# RemainingSteps 参数用于追踪和限制 reflection agent 可执行的剩余步数。
# 官方解释：
#   用于管理和记录在一个 StateGraph 中还可以执行多少步，
#   主要是为了防止图（如 agent 的反射循环）出现无限循环或超出预期的循环次数。
# 这个参数一般由调用者（如 create_reflection_graph 或运行 agent 的上层应用）指定和控制。
# 初始值通常由用户根据需要设定，例如常见初始值为 5，表示最多允许 5 轮反射循环；
#   如果不手动指定，系统可能会采用默认值（例如 5）。
from langgraph.managed import RemainingSteps
from langchain_core.messages import HumanMessage


class MessagesWithSteps(MessagesState):
    remaining_steps: RemainingSteps
    # 注意：本类本身只是把 remaining_steps 参数纳入状态，
    # 并没有在本地负责 “减一” 的逻辑。
    # 消耗 remaining_steps 的逻辑通常在主 graph 的流程控制节点或下游节点内实现，
    # 比如在主循环每轮自动减一或在特定节点专门处理。
    # https://blog.csdn.net/u013172930/article/details/147986262



def end_or_reflect(state: MessagesWithSteps) -> Literal[END, "graph"]:
    """
    判断反射循环是否继续，以下用例说明其逻辑:
    
    例1:
        state = {"remaining_steps": 1, "messages": [...]}
        因为remaining_steps < 2, 返回 END，流程终止。

    例2:
        state = {"remaining_steps": 3, "messages": []}
        因为messages为空列表, 返回 END，流程终止。

    例3:
        state = {
            "remaining_steps": 3, 
            "messages": [HumanMessage("...")]
        }
        最后一条消息是HumanMessage，返回 "graph"，继续进入主循环。

    例4:
        state = {
            "remaining_steps": 5,
            "messages": [AIMessage("...")]
        }
        最后一条消息不是HumanMessage，返回 END，流程终止。

    """

    # 为什么小于2就不用反思了？
    # 反射机制下，每进行一轮主graph → judge → reflection，再返回主graph，这需要消耗1次remaining_steps。
    # 如果remaining_steps为1，意味着只剩最后一次，进入反思环节后已无法转回主graph，不如提前终止。
    # 因此，只有当remaining_steps>=2时才允许继续进入反思判定。
    if state["remaining_steps"] < 2:
        return END

    if len(state["messages"]) == 0:
        return END
        
    last_message = state["messages"][-1]
    # 为什么最后一个消息是人类消息，就需要跳转到graph？
    # 解释：在反射（reflection）循环工作流中，"messages" 通常记录了当前的对话历程。
    # 反射机制设计为：如果上轮反思（reflection）产生了批评、建议或追问，这些都要以"用户"消息（HumanMessage）的形式
    # 反馈给主Agent（即下一轮主graph），让主Agent据此进行改进输出。
    # 因此，若最后一条消息是HumanMessage，意味着主Agent需要根据新的人类提示重新生成响应，流程应回到主graph。
    # 若不是HumanMessage（通常是AI回复），说明没有待处理的新“用户意见”，可结束流程。
    if isinstance(last_message, HumanMessage):
        return "graph"
    else:
        return END


def create_reflection_graph(
    graph: CompiledStateGraph,
    reflection: CompiledStateGraph,
    state_schema: Optional[Type[Any]] = None,
    config_schema: Optional[Type[Any]] = None,
) -> StateGraph:
    # Default to MessagesState since both subgraphs use it
    # This is the most common case for LangGraph applications
    if state_schema is None:
        _state_schema = MessagesState
    else:
        _state_schema = state_schema

    if "remaining_steps" in _state_schema.__annotations__:
        raise ValueError(
            "Has key 'remaining_steps' in state_schema, this shadows a built in key"
        )

    if "messages" not in _state_schema.__annotations__:
        raise ValueError("Missing required key 'messages' in state_schema")

    class StateSchema(_state_schema):
        remaining_steps: RemainingSteps

    rgraph = StateGraph(StateSchema, config_schema=config_schema)
    rgraph.add_node("graph", graph)
    rgraph.add_node("reflection", reflection)
    rgraph.add_edge(START, "graph")
    rgraph.add_edge("graph", "reflection")
    rgraph.add_conditional_edges("reflection", end_or_reflect)
    return rgraph
