from langchain_ollama import OllamaLLM
model = OllamaLLM(model="deepseek-r1:14b")
res = model.stream(input="介绍一下自己")
for chunk in res:
    print(chunk, end="", flush=True)