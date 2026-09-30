# streaming-chat Specification

## Purpose
TBD - created by archiving change add-chat-frontend. Update Purpose after archive.
## Requirements
### Requirement: SSE 流式端点
后端 SHALL 暴露一个流式聊天端点，以 Server-Sent Events 格式逐步返回助手回复。

#### Scenario: 流式返回回复
- **WHEN** 客户端请求流式聊天端点
- **THEN** 后端以 SSE 分片逐步返回助手回复，并在结束时分片发出完成标记

### Requirement: 流式消息持久化
后端 SHALL 在流式结束后将用户消息与完整助手回复持久化到数据库。

#### Scenario: 流式后落库
- **WHEN** 一次流式聊天结束
- **THEN** 用户消息与完整助手回复被写入数据库，可被历史端点检索

### Requirement: 流式上下文
流式端点 SHALL 与普通端点一致，携带该会话的历史消息作为上下文。

#### Scenario: 基于历史流式回复
- **WHEN** 流式请求携带会话 ID
- **THEN** 后端加载该会话历史作为上下文，并据此流式生成回复

### Requirement: CORS 支持
后端 SHALL 允许前端开发服务器跨域访问 API 端点。

#### Scenario: 跨域访问
- **WHEN** 前端从不同源（如 Vite dev server）请求后端
- **THEN** 后端返回允许跨域的 CORS 头，请求成功

