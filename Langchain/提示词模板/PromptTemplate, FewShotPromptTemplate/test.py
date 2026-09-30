from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_ollama import OllamaLLM

# 示例模板
example_template = PromptTemplate.from_template("单词：{word}，反义词：{antonym}")

# 示例的动态注入数据
example_data = [
    {"word":"大", "antonym":"小"},
    {"word":"上", "antonym":"下"},
    {"word":"长", "antonym":"短"},
    {"word":"重", "antonym":"轻"}
]

few_shot_template = FewShotPromptTemplate(
    example_prompt=example_template,
    examples=example_data,
    prefix="告知我单词的反义词，我提供如下示例：",
    suffix="基于前面的示例告诉我，{input_word}的反义词是？",
    input_variables=["input_word"]
)

model = OllamaLLM(model = "deepseek-r1:14b")
chain = few_shot_template | model
res = chain.stream(input = {"input_word":"左"})
for chunk in res:
    print(chunk, end="", flush=True)