from langchain_core.tools import tool

from RAG服务大致流程 import RagService


@tool(description="rag库向量检索参考资料")  #调取rag模块进行向量检索，并返回检索结果
def query_rag(query: str):
    return RagService().query_rag(query)

@tool(description="无参数，无返回值，只有标记作用，让ai知道已经调用了这个工具，以便于切换提示词")
def fill_context_for_report():  #让上下文有调取记录
    return "fill_context_for_report已调用"
