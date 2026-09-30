from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama

chat_prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system","你是一个诗人"),
        MessagesPlaceholder("history"),
        ("human","请再来一首诗")
    ]
)
history_data = [
    ("human","请写一首唐诗"),
    ("ai","锄禾日当午，汗滴禾下土，谁知盘中餐，粒粒皆辛苦。"),
    ("human","请写一首唐诗"),
    ("ai","西风瘦马，客输西风，西风瘦马，客输西风。"),
]
message = chat_prompt_template.invoke({"history":history_data}).to_string()
model = ChatOllama(model="deepseek-r1:14b")
res = model.stream(input = message)
for chunk in res:
    print(chunk.content, end="", flush=True)
