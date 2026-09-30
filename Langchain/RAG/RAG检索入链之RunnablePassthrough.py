from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import ChatOllama, OllamaEmbeddings

chat_model = ChatOllama(model="deepseek-r1:14b")
embeddings_model = OllamaEmbeddings(model="qwen3-embedding:4b")
chat_prompt_template= ChatPromptTemplate.from_messages(
    [
        ("system","请基于我提供的参考资料，并专业、详细地回答用户问题，参考资料:{context}"),
        ("user","用户提问:{input}")
    ]
)
vector_store = Chroma(
    collection_name="movie",
    embedding_function=embeddings_model,
    persist_directory="chromadb"
)

input_text = "我想看有关复仇的电影，请推荐我几部"

retriever = vector_store.as_retriever(search_kwargs={"k":5})

def toContext(docs:list[Document]):
    if not docs:
        return "无相关参考资料"
    context_str = "["
    for doc in docs:
        context_str += doc.page_content
    context_str += "]"
    return context_str

chain = {"input":RunnablePassthrough(),"context":retriever | toContext} | chat_prompt_template |chat_model
res = chain.stream(input_text)
for chunk in res:
    print(chunk.content, end="", flush=True)

