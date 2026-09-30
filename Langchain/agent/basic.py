from langchain.agents import create_agent
from langchain_community.chat_models import ChatTongyi
from langchain_core.tools import tool


chat_model = ChatTongyi(model="qwen3-max")

@tool(description="查询身高,不传入参数，获得结果")
def get_height() -> str:
    return "170cm"

@tool(description="查询体重,不传入参数，获得结果")
def get_weight() -> str:
    return "105kg"

agent = create_agent(
    model=chat_model,
    tools=[get_height,get_weight],
    system_prompt="你是一个聊天助手，可以回答用户问题。",
)

for chunk in agent.stream(
        {"messages":[{"role":"user","content":"查询我的BMI指数"}]},
        stream_mode="values"):
    latest_message = chunk["messages"][-1]
    if latest_message.content:
        print(type(latest_message).__name__,latest_message.content)

    try:
        if latest_message.tool_calls:
            print(f"工具调用:{[tc["name"] for tc in latest_message.tool_calls]}")
    except AttributeError as e:
        pass

