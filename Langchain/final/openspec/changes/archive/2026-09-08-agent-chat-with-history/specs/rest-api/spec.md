## ADDED Requirements

### Requirement: 会话管理端点
API SHALL 暴露会话创建、列表、删除的 HTTP 端点。

#### Scenario: 会话 CRUD
- **WHEN** 客户端调用 `POST /sessions`、`GET /sessions`、`DELETE /sessions/{id}`
- **THEN** 系统分别创建、列出、删除会话并返回相应结果

### Requirement: 聊天端点
API SHALL 暴露发送消息的端点，接收会话 ID 与用户消息，返回助手回复。

#### Scenario: 发送消息
- **WHEN** 客户端向指定会话发送一条用户消息
- **THEN** 系统持久化消息、调用 Agent 生成回复，并返回助手回复与消息记录

### Requirement: 历史端点
API SHALL 暴露获取会话消息历史的端点。

#### Scenario: 获取历史
- **WHEN** 客户端请求 `GET /sessions/{id}/messages`
- **THEN** 系统按时间正序返回该会话的完整消息历史

### Requirement: 请求校验
API SHALL 对请求进行校验，拒绝缺失或非法的参数。

#### Scenario: 非法参数被拒绝
- **WHEN** 客户端提交缺失会话 ID 或空消息的请求
- **THEN** 系统返回 422 校验错误
