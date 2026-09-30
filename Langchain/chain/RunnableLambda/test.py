from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda
from langchain_ollama import ChatOllama

chat_prompt_template_1 = ChatPromptTemplate.from_messages(
    [
        ("system","你是一个诗人"),
        MessagesPlaceholder("history"),
        ("human","请再来一首诗,仅生成一首诗，且不要有额外的内容")
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
        ("human","这首诗为{poem}，帮我解析这首诗"),
    ]
)

model = ChatOllama(model="deepseek-r1:14b")
#将方法转换为继承Runnable类的子类
ToPoem = RunnableLambda(lambda ai_msg: {"poem":ai_msg.content}) #AIMessage转dict
chain = chat_prompt_template_1 | model | ToPoem | chat_prompt_template_2 | model
res = chain.stream(input={"history":history_data})
for chunk in res:
    print(chunk.content, end="", flush=True)
