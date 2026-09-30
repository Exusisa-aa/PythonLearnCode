## Context

后端已有会话 CRUD 与非流式聊天端点（见 `agent-chat-with-history` 变更），但无 UI。需新增 Vue 3 + Vite 前端，并提供 SSE 流式聊天能力以支持打字机效果。前端开发用 Vite dev server 代理后端，生产可由 FastAPI 托管构建产物。

## Goals / Non-Goals

**Goals:**
- 交付一个精美、可交互的聊天前端（会话管理 + 聊天 + 流式显示）。
- 后端提供 SSE 流式端点，前端消费流式分片实现打字机效果。
- 开发环境可独立运行前端并连通后端（CORS + 代理）。

**Non-Goals:**
- 不做用户认证、多用户隔离。
- 不做前端自动化测试框架搭建（MVP 以手动验证为主）。
- 不做消息分页、会话重命名/搜索等增强功能。

## Decisions

### 1. 前端独立工程 `frontend/`，Vue 3 + Vite + Composition API
- **决策**：`frontend/` 作为独立 npm 工程，使用 `<script setup>` 组合式 API，状态用 Vue 自带 `ref`/`reactive` 管理（不引入 Pinia/Vuex）。
- **备选**：纯静态单页、React。
- **理由**：用户指定 Vue 3 + Vite；Composition API 是当前主流写法；MVP 状态简单，无需引入 Pinia。

### 2. 流式端点用 SSE（`sse-starlette`），新增独立端点而非改造旧端点
- **决策**：新增 `POST /sessions/{id}/messages/stream`，返回 `text/event-stream`；复用 `agent/graph` 的模型流式调用。
- **备选**：把现有 `POST /sessions/{id}/messages` 改为流式；WebSocket。
- **理由**：保留旧端点向后兼容；SSE 单向流足够聊天场景，比 WebSocket 简单、对 HTTP 友好；`sse-starlette` 与 FastAPI 集成成熟。

### 3. 模型层暴露 `stream` 能力
- **决策**：在 `agent/graph.py` 增补一个流式调用函数，利用 `ChatOllama.stream(messages)` 逐 chunk 产出 token；图仍保留 `invoke`（非流式端点复用）。
- **理由**：SSE 端点需要 token 粒度分片；复用同一 LLM 实例，避免重复配置。

### 4. 流式消息的持久化时机
- **决策**：流式开始前先落库用户消息；流式过程中累积助手文本；流式结束（含正常与异常）后把完整助手回复一次性落库。
- **理由**：保证历史端点始终拿到完整助手回复（而非半截），且与现有数据模型一致；异常时也能留下用户消息与已生成部分。

### 5. CORS + 开发代理
- **决策**：后端用 `fastapi.middleware.cors.CORSMiddleware` 允许 `http://localhost:5173`；前端 Vite `server.proxy` 将 `/sessions` 与 `/api` 请求代理到后端 8000，前端代码统一用相对路径。
- **理由**：开发阶段两者同源代理最省心（无需前端写死后端地址），CORS 作为直连兜底；生产托管构建产物时同源，无需 CORS。

### 6. 前端 API 客户端与 SSE 消费
- **决策**：`fetch` 走普通 REST；流式端点用 `fetch` + `ReadableStream` 解析 SSE 分片（手写轻量解析，不引第三方 SSE 库）。
- **理由**：避免为单个端点引入额外依赖；`fetch` 原生支持流式读取。

### 7. 样式方案
- **决策**：手写 CSS（组件 scoped style），不引 UI 框架；配色采用现代聊天产品风格（深色侧栏 + 浅色对话区）。
- **理由**：轻量、可控、无额外依赖，符合「精美但精简」目标。

## Risks / Trade-offs

- **[`deepseek-r1:14b` 首 token 延迟高]** → 打字机效果可能等待较久才开始；前端在等待期间显示「思考中」占位动画，并保留旧端点作为无流式兜底。
- **[SSE 手动解析的健壮性]** → 自写解析器需处理分块边界；用换行分隔的 SSE 协议，解析逻辑简单，风险可控。
- **[流式中途断连导致消息不全]** → 异常路径仍落库已生成部分，避免丢消息。
- **[前端构建产物托管与 dev server 双模式]** → 明确两套启动方式，文档说明，避免混淆。

## Migration Plan

无数据库迁移。部署/运行步骤：
1. 后端新增 `sse-starlette` 依赖并安装。
2. 实现流式端点与 CORS。
3. 创建 `frontend/`，`npm install`，`npm run dev` 启动开发服务器。
4. 生产：`npm run build` 产出 `dist/`，由 FastAPI 静态托管。

## Open Questions

- 是否需要会话重命名 / 搜索？
- 是否需要「停止生成」按钮（中断流式）？
