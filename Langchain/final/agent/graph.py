from langchain_ollama import ChatOllama
from langgraph.graph import END, START, MessagesState, StateGraph

from final.config.settings import settings

llm = ChatOllama(model=settings.OLLAMA_MODEL)


def call_model(state: MessagesState) -> dict:
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


def stream_model(messages: list):
    """逐 token 流式产出回复文本。"""
    for chunk in llm.stream(messages):
        content = chunk.content
        if content:
            yield content


graph_builder = StateGraph(MessagesState)
graph_builder.add_node("call_model", call_model)
graph_builder.add_edge(START, "call_model")
graph_builder.add_edge("call_model", END)

agent_graph = graph_builder.compile()
