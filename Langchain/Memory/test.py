from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from typing import Annotated
from typing_extensions import TypedDict
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage

# 1. 模型
model = ChatOllama(model="deepseek-r1:14b")

# 2. 定义状态：messages 存放全部对话历史
class State(TypedDict):
    messages: Annotated[list, add_messages]


def chatbot_node(state: State):
    """聊天节点：拼接system提示 + 历史消息，调用ollama"""
    # system提示，等价你原来prompt里的system:"你需要根据历史会话记录回答用户问题。对话历史："
    sys_msg = SystemMessage(content="你需要根据历史会话记录回答用户问题。对话历史：")
    # 把system拼在最前面，后面跟用户、模型历史消息
    all_messages = [sys_msg] + state["messages"]
    resp = model.invoke(all_messages)
    return {"messages": [resp]}


# 3. 构建graph
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot_node)
graph_builder.add_edge(START, "chatbot")

# 内存checkpoint，替代 InMemoryChatMessageHistory
memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)


if __name__ == "__main__":
    # thread_id 等价原来 session_id
    session_config = {
        "configurable": {
            "thread_id": "user_002"
        }
    }

    def stream_query(user_input: str):
        """封装流式调用，模拟你原来的conversation_chain.stream"""
        for chunk in graph.stream(
            {"messages": [("user", user_input)]},
            config=session_config,
            stream_mode="values"
        ):
            # 取最新ai输出
            last_msg = chunk["messages"][-1]
            if hasattr(last_msg, "content"):
                print(last_msg.content, end="", flush=True)
        print("\n")

    # 和原来完全一样的三轮提问
    stream_query("小明有两只猫")
    stream_query("小明有一条狗")
    stream_query("小明有几只宠物")
