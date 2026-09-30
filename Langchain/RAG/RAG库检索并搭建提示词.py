from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
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

input_text = "我想看有关家庭的电影，请推荐我几部"

results = vector_store.similarity_search(input_text,5)
reference_text = "["
for doc in results:
    reference_text += doc.page_content
reference_text += "]"

print("用户提问:"+input_text)
print("参考文献:"+reference_text)

chain = chat_prompt_template | chat_model
res = chain.stream({"input":input_text,"context":reference_text})
for chunk in res:
    print(chunk.content, end="", flush=True)
