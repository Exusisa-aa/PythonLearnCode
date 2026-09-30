## 1. 项目骨架与依赖

- [x] 1.1 创建分层目录结构（`config` / `db` / `agent` / `api`）
- [x] 1.2 编写依赖清单（langchain、langgraph、langchain-ollama、fastapi、uvicorn、sqlalchemy、asyncpg、pydantic-settings、python-dotenv）

## 2. 配置加载

- [x] 2.1 实现 `Settings(BaseSettings)`，从 `.env` 读取 `PG_*` 与 `OLLAMA_MODEL`

## 3. 数据库层

- [x] 3.1 定义 `Base` 及 `Session` / `Message` 模型（`messages.session_id` 外键 + `ondelete=CASCADE`）
- [x] 3.2 实现异步引擎与 `async_sessionmaker` 工厂
- [x] 3.3 实现会话仓储：创建、按最近更新倒序列出、删除（含 404 判定）
- [x] 3.4 实现消息仓储：保存一轮对话、按会话 ID 正序读取历史

## 4. Agent 执行

- [x] 4.1 用 LangChain 初始化 Ollama 模型（模型名来自配置）
- [x] 4.2 用 LangGraph 定义 `StateGraph`：`call_model` 节点 + `MessagesState`，边 `START -> call_model -> END`

## 5. API 层

- [x] 5.1 定义 Pydantic 请求/响应 schema（含空消息与缺失字段校验）
- [x] 5.2 实现会话管理端点：`POST /sessions`、`GET /sessions`、`DELETE /sessions/{id}`
- [x] 5.3 实现聊天端点：`POST /sessions/{id}/messages`（持久化→调用 Agent→返回助手回复）
- [x] 5.4 实现历史端点：`GET /sessions/{id}/messages`

## 6. 入口与集成

- [x] 6.1 实现 `main.py` 应用入口与启动建表
- [x] 6.2 端到端验证：启动服务，走通「创建会话 → 发送消息 → 查询历史」
