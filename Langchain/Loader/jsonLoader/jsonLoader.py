from langchain_community.document_loaders import JSONLoader

loader = JSONLoader(
    file_path="tset.json",
    jq_schema=".",
    text_content=False
)

for document in loader.lazy_load():
    print(document)