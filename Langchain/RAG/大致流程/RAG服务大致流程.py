from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import ChatOllama, OllamaEmbeddings
from 向量库服务大致流程 import VectorStoreService
from utils.config_handler import agent_conf,rag_conf

chat_model = ChatOllama(model=agent_conf["chat_model"])
embeddings_model = OllamaEmbeddings(model=rag_conf["embeddings_model"])
class RagService(object):
    def __init__(self):
        self.vector_service = VectorStoreService(embeddings_model=embeddings_model)
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", "请基于我提供的参考资料，并专业、详细地回答用户问题，参考资料:{context}"),
                ("user", "用户提问:{input}")
            ]
        )
        self.chat_model = chat_model
        self.chain = self.get_chain()

    def get_chain(self):
        retriever = self.vector_service.get_retriever()

        def toContext(docs: list[Document]):
            if not docs:
                return "无相关参考资料"
            context_str = "["
            for doc in docs:
                context_str += f"文档片段：{doc.page_content}\n文档元数据：{doc.metadata}\n\n"
            context_str += "]"
            return context_str

        chain = {"input":RunnablePassthrough(),"context": retriever | toContext} | self.prompt_template | self.chat_model

        return chain

    def query_rag(self,query: str):
        return self.chain.stream(query)

