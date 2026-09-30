from langchain.agents.middleware import wrap_tool_call, dynamic_prompt
from langgraph.prebuilt.tool_node import ToolCallRequest

from utils.prompt_loader import load_report_prompts, load_system_prompts


@wrap_tool_call
def tool_call_hook(request,handler):
    if request.tool_call["name"] == "fill_context_for_report":
        request.runtime.context["report"] = True  #若有调用这个工具的记录，则把上下文中key为report的值标记成True
    return request(handler)

@dynamic_prompt #每次提问大模型都会执行一次，在这个注解方法里返回提示词模版，会动态加入大模型的上下文中
def report_prompt_switch(request):
    is_report = request.runtime.context.get("report",False)
    if is_report:
        return load_report_prompts()
    return load_system_prompts()