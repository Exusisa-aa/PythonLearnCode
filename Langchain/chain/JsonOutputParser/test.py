from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama

chat_prompt_template_1 = ChatPromptTemplate.from_messages(
    [
        ("system","你是一个诗人"),
        MessagesPlaceholder("history"),
        ("human","请再来一首诗,将这首诗封装为JSON对象，"
                 "其中key分别为title和poem，对应诗的标题和内容，严格遵循")
    ]
)
history_data = [
    ("human","请写一首唐诗"),
    ("ai","锄禾日当午，汗滴禾下土，谁知盘中餐，粒粒皆辛苦。"),
    ("human","请写一首唐诗"),
    ("ai","西风瘦马，客输西风，西风瘦马，客输西风。"),
]
chat_prompt_template_2 = ChatPromptTemplate.from_messages(
    [
        ("system","你是一个诗人"),
        ("human","诗的标题为{title}，诗的内容为{poem}，帮我解析这首诗"),
    ]
)

parser = JsonOutputParser()
model = ChatOllama(model="deepseek-r1:14b")
# history -> promptValue -> AIMessage:JSON -> dict:JSON -> promptValue -> AIMessage
chain = chat_prompt_template_1 | model | parser | chat_prompt_template_2 | model
res = chain.stream(input={"history":history_data})
for chunk in res:
    print(chunk.content, end="", flush=True)
