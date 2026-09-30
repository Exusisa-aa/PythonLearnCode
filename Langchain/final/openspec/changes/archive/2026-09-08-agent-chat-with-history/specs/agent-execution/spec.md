## ADDED Requirements

### Requirement: 多轮上下文对话
Agent SHALL 在生成回复时携带该会话的历史消息作为上下文，以维持多轮对话的连贯性。

#### Scenario: 基于历史回复
- **WHEN** 用户在同一会话内发送与之前消息相关的追问
- **THEN** Agent 基于会话历史上下文生成连贯的回复

### Requirement: Agent 流程控制
系统 SHALL 使用 LangGraph 定义 Agent 执行流程，协调模型调用与后续步骤。

#### Scenario: 执行对话流程
- **WHEN** 一次聊天请求进入 Agent
- **THEN** LangGraph 流程执行模型调用并产出助手回复

### Requirement: 模型后端配置
系统 SHALL 从配置加载模型后端（默认 Ollama）与模型名称，并据此初始化 LangChain 模型。

#### Scenario: 使用配置的模型
- **WHEN** 系统启动并处理聊天请求
- **THEN** 使用 `.env` 中配置的 Ollama 模型生成回复
