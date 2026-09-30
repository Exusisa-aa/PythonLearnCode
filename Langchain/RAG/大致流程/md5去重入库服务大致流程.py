import hashlib
import os
from datetime import datetime
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from utils.config_handler import rag_conf, chroma_conf

embeddings_model = OllamaEmbeddings(model=rag_conf["embeddings_model"])

def get_string_md5(input_str: str,encoding='utf-8'):
    str_bytes = input_str.encode(encoding=encoding)
    md5_obj = hashlib.md5()
    md5_obj.update(str_bytes)
    md5_hex = md5_obj.hexdigest()
    return md5_hex

def check_md5(md5_str: str):
    if not os.path.exists("./data.txt"):
        open("./data.txt",'w',encoding="utf-8").close()
        return False
    else:
        for line in open("./data.txt","r",encoding="utf-8").readlines():
            line = line.strip()
            if line == md5_str:
                return True
        return False

def save_md5(md5_str: str):
    with open("./data.txt",'a',encoding="utf-8") as f:
        f.write(md5_str + '\n')

class KnowledgeBaseService(object):
    def __init__(self):
        self.chroma = Chroma(
            collection_name=chroma_conf["collection_name"],
            embedding_function=embeddings_model,
            persist_directory=chroma_conf["persist_directory"]
        )
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=rag_conf["chunk_size"],
            chunk_overlap=rag_conf["chunk_overlap"],
            separators=rag_conf["separators"],
            length_function=rag_conf["length_function"]
        )

    def upload_by_str(self,data:str,filename):
        hex = get_string_md5(data)
        if check_md5(hex):
            return "[跳过]内容已存在"
        if len(data) > 1000:
            knowledge_chunks:list[str] = self.splitter.split_text(data)
        else:
            knowledge_chunks = [data]
        metadata = {
            "source":filename,
            "create_time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator":"小曹"
        }
        self.chroma.add_texts(
            knowledge_chunks,
            metadatas=[metadata for _ in knowledge_chunks]
        )
        save_md5(hex)
if __name__ == '__main__':
    print(get_string_md5("周杰伦"))
    print("\n")
    save_md5("7a8941058aaf4df5147042ce104568da")
    print(check_md5("7a8941058aaf4df5147042ce104568da"))