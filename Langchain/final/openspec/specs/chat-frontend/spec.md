# chat-frontend Specification

## Purpose
TBD - created by archiving change add-chat-frontend. Update Purpose after archive.
## Requirements
### Requirement: 会话列表展示
前端 SHALL 展示所有会话，按最近更新时间倒序排列，并允许用户选择当前会话。

#### Scenario: 显示会话列表
- **WHEN** 页面加载或会话发生变化
- **THEN** 前端从后端获取会话列表并倒序展示，用户可点击选择

### Requirement: 新建会话
前端 SHALL 提供新建会话的入口，创建后立即切换为该会话并显示空聊天窗口。

#### Scenario: 创建会话
- **WHEN** 用户点击「新建会话」
- **THEN** 前端调用创建接口，新会话出现在列表顶部并成为当前会话

### Requirement: 删除会话
前端 SHALL 提供删除会话的入口，删除后刷新列表并清空聊天窗口。

#### Scenario: 删除会话
- **WHEN** 用户删除当前会话
- **THEN** 前端调用删除接口，该会话从列表移除，聊天窗口清空

### Requirement: 消息展示
前端 SHALL 在聊天窗口中以气泡形式展示用户与助手的消息，并按时间正序排列。

#### Scenario: 展示历史消息
- **WHEN** 用户选中某会话
- **THEN** 前端加载并正序展示该会话的完整历史消息

### Requirement: 发送消息
前端 SHALL 提供输入框与发送按钮，将用户消息发送到当前会话。

#### Scenario: 发送用户消息
- **WHEN** 用户在输入框输入内容并发送
- **THEN** 前端展示用户消息并请求助手回复

### Requirement: 流式回复显示
前端 SHALL 以打字机方式逐步显示助手回复，而非等待完整结果一次性出现。

#### Scenario: 流式显示
- **WHEN** 助手回复以流式分片到达
- **THEN** 前端将分片逐段追加到当前助手气泡中，直至结束

### Requirement: 错误提示
前端 SHALL 在请求失败时给出可见的错误提示。

#### Scenario: 请求失败
- **WHEN** 后端请求返回错误或网络异常
- **THEN** 前端显示错误提示，不阻塞用户后续操作

