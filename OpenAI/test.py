from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

# 调用时加上 stream=True
# noinspection PyTypeChecker
response = client.chat.completions.create(
    model="deepseek-r1:14b",  # 请替换为你实际正确的模型名称
    messages=[
        {"role": "system", "content": "你是一个Python编程专家，并且不说废话简单回答"},
        {"role": "assistant", "content": "我是Python专家，并且话不多，你要问什么？"},
        {"role": "user", "content": "输入1-10的数字，使用Python"}
    ],
    temperature=0.7,
    stream=True            # 开启流式输出
)

# 逐块读取并打印响应
for chunk in response:
    # 获取当前块的内容（思考过程或最终回答都在这里）
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="", flush=True)