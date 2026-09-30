## Why

当前 `final` 目录只是一个空骨架，还没有一个可运行的应用。我们需要一个具备「多轮对话 + 历史记录持久化」的 Agent 聊天后端，让用户能够与 LLM Agent 连续对话，且会话与消息历史可跨请求持久化、可随时恢复——这是后续所有 LangChain/LangGraph 学习与实验的基础底座。

## What Changes

- 新增一个基于 **FastAPI** 的后端服务，对外暴露会话与聊天的 REST 接口。
- 新增基于 **LangChain + LangGraph** 的 Agent 执行流程，支持多轮对话与工具调用。
- 新增基于 **PostgreSQL** 的持久化层，保存会话与消息历史（连接信息从 `.env` 读取）。
- 新增配置加载模块，统一从 `.env` 读取数据库连接与模型配置。
- 集成 **Ollama**（`deepseek-r1:14b`）作为默认模型后端。

## Capabilities

### New Capabilities

- `conversation-history`: 会话与消息历史的持久化、检索与管理（创建/列出/删除会话，读取某会话的完整消息记录）。
- `agent-execution`: 基于 LangChain + LangGraph 的 Agent 执行流程，支持多轮上下文与工具调用。
- `rest-api`: FastAPI 后端接口层，暴露会话管理与会话聊天的 HTTP 端点。

### Modified Capabilities

<!-- 无现有 capability，留空 -->

## Impact

- **新增代码**：全新应用，全部为新增模块（配置、数据库模型/仓储、Agent 图、API 路由、入口）。
- **新增依赖**：`langchain`、`langgraph`、`langchain-ollama`、`fastapi`、`uvicorn`、`sqlalchemy`（异步）、`asyncpg`、`pydantic-settings`、`python-dotenv`。
- **环境**：依赖 `.env` 中的 `PG_*` 与 `OLLAMA_MODEL` 配置；需本地 PostgreSQL（库名 `langgraph_chat`）与 Ollama 服务可用。
- **API**：新增一组 REST 端点（会话 CRUD、发送消息、获取历史）。
