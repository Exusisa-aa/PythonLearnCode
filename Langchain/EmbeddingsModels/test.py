from langchain_ollama import OllamaEmbeddings
model = OllamaEmbeddings(model="qwen3-embedding:4b")
print(model.embed_query("你好"))
print(model.embed_documents(["你好","世界","随便"]))