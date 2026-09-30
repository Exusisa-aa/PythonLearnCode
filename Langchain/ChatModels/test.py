from langchain_ollama import ChatOllama
model = ChatOllama(model="deepseek-r1:14b")
messages = [
    ("system","你是一个诗人"),
    ("human","写一首唐诗"),
    ("ai","锄禾日当午，汗滴禾下土，谁知盘中餐，粒粒皆辛苦。"),
    ("human","按照上一个格式，写一首唐诗")
]
res = model.stream(input=messages)
for chunk in res:
    print(chunk.content, end="", flush=True)