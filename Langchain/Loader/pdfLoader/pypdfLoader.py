from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader(
    file_path="test.pdf",
    mode="page",
    # password="123"
)

for document in loader.lazy_load():
    print(document)
    print(10*"-")