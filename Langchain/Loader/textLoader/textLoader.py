from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

loader = TextLoader(
    file_path="test.txt",
    encoding="utf-8"
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n","\n","。","!","?",".","！","?"," ",""],
    length_function=len
)

splitDocs = splitter.split_documents(loader.load())

for doc in splitDocs:
    print("-"*10)
    print(doc)
    print("-"*10)