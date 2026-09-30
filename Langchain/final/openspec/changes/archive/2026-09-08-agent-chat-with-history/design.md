## Context

`final` 目录当前为空骨架，仅含 `.env`（PostgreSQL 连接信息 + Ollama 模型名）。需从零构建一个带历史记录的 Agent 聊天后端。技术栈约束来自用户：基础库 LangChain、流程控制 LangGraph、后端 FastAPI、数据库连接信息在 `.env`。

## Goals / Non-Goals

**Goals:**
- 提供可运行的 FastAPI 服务，暴露会话管理与会话聊天的 REST 接口。
- 用 LangGraph 编排 Agent 执行，用 LangChain 承载模型与消息抽象。
- 用 PostgreSQL 持久化会话与消息，历史可跨请求恢复。
- 配置从 `.env` 读取，模型后端默认为 Ollama（`deepseek-r1:14b`）。

**Non-Goals:**
- MVP 不含具体工具（tool）的接入；LangGraph 图结构为其预留扩展点，但本期只做「模型调用」节点。
- 不含用户认证、多租户、流式（SSE）输出、消息分页。
- 不含数据库迁移工具（Alembic）；本期用启动时 `create_all` 建表。

## Decisions

### 1. 历史记录自建存储，而非 LangGraph checkpointer
- **决策**：用 SQLAlchemy 自建 `sessions` / `messages` 两张表，请求时从库中加载历史消息，组装为消息列表传入 LangGraph 图。
- **备选**：使用 LangGraph 自带的持久化（如 `PostgresSaver` checkpoint）。
- **理由**：本需求要求对外提供会话 CRUD 与「按会话 ID 取完整历史」的 API，自建存储能直接、可控地满足查询需求；checkpointer 面向图状态恢复，不适合作为历史查询数据源，且两者混用会带来两份状态的同步复杂度。

### 2. LangGraph 用 StateGraph + MessagesState 单节点
- **决策**：图含一个 `call_model` 节点，状态用 `MessagesState`（`messages` 列表），边 `START -> call_model -> END`。
- **理由**：MVP 只需「带上下文生成回复」；单节点 + `MessagesState` 是 LangGraph 最小可用形态，后续加工具时只需把 `call_model` 替换为 `agent` 节点并在工具分支循环即可，迁移成本低。

### 3. 数据模型：sessions 1—N messages，级联删除
- **决策**：`sessions(id, created_at, updated_at)`，`messages(id, session_id FK, role, content, created_at)`；`messages.session_id` 设 `ondelete=CASCADE`。
- **理由**：满足「删除会话级联删除消息」的 spec 要求；`updated_at` 支撑「按最近更新排序」的列表需求（发消息时更新会话时间）。

### 4. 配置用 pydantic-settings 加载
- **决策**：`Settings(BaseSettings)` 读取 `PG_*` 与 `OLLAMA_MODEL`，通过 `env_file=".env"` 注入。
- **理由**：类型安全、集中管理，避免散落的 `os.getenv`；与 FastAPI/Pydantic 生态一致。

### 5. 数据库访问用 SQLAlchemy 2.0 异步 + asyncpg
- **决策**：`create_async_engine` + `async_sessionmaker` + asyncpg 驱动，FastAPI 通过依赖注入提供 session。
- **理由**：FastAPI 原生异步，异步驱动避免阻塞事件循环；asyncpg 是 PostgreSQL 高性能异步驱动。

### 6. 分层结构
- **决策**：`config` / `db`（模型+仓储）/ `agent`（图）/ `api`（路由+schemas）/ `main` 五层。
- **理由**：职责清晰，便于后续扩展工具、迁移、测试。

## Risks / Trade-offs

- **[无迁移工具，`create_all` 建表]** → 表结构演进需手动处理；MVP 可接受，后续引入 Alembic。
- **[Ollama 本地模型响应慢 / 不可用]** → 启动或请求时可能超时；在配置与错误处理中给出明确报错信息。
- **[每次请求全量加载历史]** → 长会话上下文变长、成本上升；本期无分页，后续可引入消息分页/摘要。
- **[单节点图与「工具调用」措辞不一致]** → proposal 提及工具调用，但 spec 未单列该需求；本期以 spec 为准，工具作为 Non-Goal 预留。

## Migration Plan

全新应用，无迁移。部署步骤：
1. 确保本地 PostgreSQL（库 `langgraph_chat`）与 Ollama（`deepseek-r1:14b`）可用。
2. 安装依赖（`requirements.txt` / `pyproject.toml`）。
3. 配置 `.env`。
4. 启动服务，首次启动自动建表。

## Open Questions

- 是否需要在 MVP 阶段就接入具体工具（如搜索/计算）？
- 是否需要流式（SSE）输出？
