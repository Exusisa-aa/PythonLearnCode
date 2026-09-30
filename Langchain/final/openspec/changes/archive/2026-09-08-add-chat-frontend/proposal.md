## Why

后端（FastAPI + LangGraph + PostgreSQL）已经具备会话管理与聊天能力，但目前只能通过 `/docs` 或命令行测试，缺少面向用户的界面。需要一个精美的前端，让用户能直观地创建会话、进行多轮对话、查看历史，并看到流式（打字机）回复效果。

## What Changes

- 新增一个 **Vue 3 + Vite** 前端工程（位于 `frontend/`），提供会话管理与聊天界面。
- 前端支持：会话列表、新建/删除会话、聊天窗口、历史消息展示、流式（打字机）回复显示。
- 后端新增 **SSE 流式聊天端点**，支持助手回复逐段流式返回。
- 后端启用 **CORS**，允许前端开发服务器跨域访问。
- 保留现有非流式端点不变，向后兼容。

## Capabilities

### New Capabilities

- `chat-frontend`: 基于 Vue 3 + Vite 的聊天前端，覆盖会话管理与聊天交互的 UI。
- `streaming-chat`: 后端 SSE 流式聊天端点，以及前端对流式响应的消费。

### Modified Capabilities

<!-- 现有 rest-api 端点行为不变，仅新增能力，无需 delta -->

## Impact

- **新增代码**：全新前端工程 `frontend/`（Vue 组件、状态管理、样式）；后端新增流式路由。
- **修改代码**：`api/routes.py`（新增流式端点）、`agent/graph.py`（暴露支持流式调用的能力）、`main.py`（挂载 CORS 与前端静态托管）。
- **新增依赖**：后端 `sse-starlette`（SSE 支持）；前端 `vue`、`vite`、`@vitejs/plugin-vue` 等（由 `frontend/package.json` 管理）。
- **环境**：开发时 Vite dev server（默认 5173）通过代理访问后端 8000；生产可由 FastAPI 托管前端构建产物。
