from langchain_community.document_loaders import CSVLoader

loader = CSVLoader(
    file_path="tmdb.csv",
    csv_args={
        "delimiter":",",
        "quotechar":'"',
        # "fieldnames":['name','age',...]  表头
    },
    encoding="utf-8"
)

# for document in loader.load():
#     print(document)

for document in loader.lazy_load():
    print(document)