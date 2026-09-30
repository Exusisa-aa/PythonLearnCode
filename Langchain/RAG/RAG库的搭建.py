from langchain_chroma import Chroma
from langchain_community.document_loaders import CSVLoader
from langchain_ollama import OllamaEmbeddings

model = OllamaEmbeddings(model="qwen3-embedding:4b")

vector_store = Chroma(
    collection_name="movie",
    embedding_function=model,
    persist_directory="chromadb"
)

# loader = CSVLoader(
#     file_path="csv/tmdb.csv",
#     csv_args={
#         "delimiter": ",",
#         "quotechar": '"',
#     },
#     encoding="utf-8",
#     source_column="电影名"
# )
#
# documents = loader.load()
#
# vector_store.add_documents(
#     documents=documents,
#     ids=["ids"+str(i) for i in range(1,len(documents)+1)]
# )
#
# vector_store.delete(["ids1","ids2"])

result = vector_store.similarity_search(
    "复仇",
    5,
    # filter={"source":"肖申克的救赎"}
)

print(result)