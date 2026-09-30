## 1. 后端流式能力

- [x] 1.1 新增依赖 `sse-starlette` 并安装
- [x] 1.2 在 `agent/graph.py` 增补流式调用函数（复用 `ChatOllama.stream`）
- [x] 1.3 新增 SSE 流式端点 `POST /sessions/{id}/messages/stream`
- [x] 1.4 流式开始前落库用户消息，结束后落库完整助手回复
- [x] 1.5 在 `main.py` 启用 CORS（允许 5173 开发源）

## 2. 前端工程初始化

- [x] 2.1 创建 `frontend/` 工程（`package.json`、`vite.config.js`、入口 `index.html`、`src/main.js`）
- [x] 2.2 配置 Vite 代理与 `@vitejs/plugin-vue`
- [x] 2.3 编写基础样式（深色侧栏 + 浅色对话区布局）

## 3. 前端核心功能

- [x] 3.1 实现 API 客户端（会话 CRUD + 历史 + 流式消费）
- [x] 3.2 实现会话列表组件（展示、新建、删除、选中）
- [x] 3.3 实现聊天窗口组件（消息气泡 + 历史加载）
- [x] 3.4 实现消息输入与发送
- [x] 3.5 实现流式（打字机）回复显示与「思考中」占位
- [x] 3.6 实现错误提示

## 4. 集成与验证

- [x] 4.1 后端与前端联调：创建会话 → 发送消息 → 流式显示 → 查看历史
- [x] 4.2 生产模式验证：`npm run build` 产物由 FastAPI 托管访问
