from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_ollama import ChatOllama

model = ChatOllama(model="deepseek-r1:14b")
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你需要根据历史会话记录回答用户问题。对话历史："),
        MessagesPlaceholder("chat_history"),
        ("human", "请回答以下问题，{input}")
    ]
)

base_chain = prompt | model

store = {}

def get_history(session_id):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

conversation_chain = RunnableWithMessageHistory(
    base_chain,
    get_history,
    input_messages_key="input",
    history_messages_key="chat_history"
)

if __name__ == "__main__":
    session_config = {
        "configurable" :{
            "session_id":"user_002"
        }
    }

    res1 = conversation_chain.stream({"input":"小明有两只猫"},session_config)
    for chunk in res1:
        print(chunk.content, end="", flush=True)
    print("\n")
    res2 = conversation_chain.stream({"input": "小明有一条狗"}, session_config)
    for chunk in res2:
        print(chunk.content, end="", flush=True)
    print("\n")
    res3 = conversation_chain.stream({"input": "小明有几只宠物"}, session_config)
    for chunk in res3:
        print(chunk.content, end="", flush=True)
    print("\n")