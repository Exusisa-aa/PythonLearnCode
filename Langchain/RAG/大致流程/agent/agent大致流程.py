from langchain.agents import create_agent
from langchain_community.chat_models import ChatTongyi

from tools.middleware import tool_call_hook, report_prompt_switch
from tools.rag_tool import query_rag
from utils.config_handler import agent_conf


class ReactAgent:
    def __init__(self):
        self.agent = create_agent(
            model=ChatTongyi(model=agent_conf["tool_model"]),
            system_prompt="你是一个聊天助手，可以回答用户问题。",
            tools=[query_rag], #fill_context_for_report
            # middleware=[tool_call_hook,report_prompt_switch]
        )

    def execute_stream(self,query):
        for chunk in self.agent.stream(
                {
                    "messages":[
                        {"role": "user", "content": query},
                    ]
                },
                stream_mode="values"): #context={"report":False}
            latest_message = chunk["messages"][-1]
            if latest_message.content:
                print(type(latest_message).__name__, latest_message.content)

            try:
                if latest_message.tool_calls:
                    print(f"工具调用:{[tc["name"] for tc in latest_message.tool_calls]}")
            except AttributeError as e:
                pass


if __name__ == '__main__':
    agent = ReactAgent()
    agent.execute_stream("我想看有关复仇的电影，请推荐我几部")