from langchain_community.vectorstores import Chroma

from utils.config_handler import chroma_conf


class VectorStoreService(object):
    def __init__(self,embeddings_model):
        self.embedding = embeddings_model
        self.vector_store = Chroma(
            collection_name=chroma_conf["collection_name"],
            embedding_function=embeddings_model,
            persist_directory=chroma_conf["persist_directory"]
        )

    def get_retriever(self):
        return self.vector_store.as_retriever(search_kwargs={"k":3})

