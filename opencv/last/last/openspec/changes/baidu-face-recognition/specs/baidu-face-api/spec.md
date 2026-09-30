## ADDED Requirements

### Requirement: Access Token 获取与缓存

系统 SHALL 使用配置中的 API Key 与 Secret Key 调用 `https://aip.baidubce.com/oauth/2.0/token` 换取 `access_token`，并缓存该 token 及其过期时间以避免重复获取。缓存有效期 SHALL 按 30 天设置并留出提前刷新余量。

#### Scenario: 首次调用时获取 token

- **WHEN** 客户端首次发起需要鉴权的业务请求且本地无可用 token
- **THEN** 系统先向 token 接口发起请求，取得 `access_token` 后将其缓存，再携带该 token 执行业务请求

#### Scenario: token 仍在有效期内复用

- **WHEN** 客户端发起业务请求且缓存中的 token 尚未过期
- **THEN** 系统直接复用缓存中的 token，不重复调用 token 接口

#### Scenario: token 失效时自动重取并重试

- **WHEN** 业务请求返回错误码 `110`（token 无效）或 `111`（token 过期）
- **THEN** 系统清除缓存、重新获取 token，并自动重试原业务请求一次

#### Scenario: 凭据缺失时给出明确报错

- **WHEN** 配置中缺少 API Key 或 Secret Key
- **THEN** 系统在启动阶段即报错并提示使用者填写 `.env`，而不是在后续请求时抛出难以理解的异常

### Requirement: 图片编码为 Base64

系统 SHALL 支持将本地图片文件和 OpenCV 采集到的图像帧编码为百度接口所需的 Base64 字符串，编码结果 MUST NOT 包含 `data:image/jpg;base64,` 之类的 Data URI 前缀。

#### Scenario: 编码本地图片文件

- **WHEN** 传入一个受支持格式（PNG/JPG/JPEG/BMP）的本地图片文件路径
- **THEN** 系统读取文件并返回其 Base64 编码字符串

#### Scenario: 编码摄像头采集的帧

- **WHEN** 传入一帧 OpenCV 的 BGR `ndarray` 图像数据
- **THEN** 系统将其编码为 JPEG 字节流后再转为 Base64 字符串返回

#### Scenario: 编码结果不含 Data URI 前缀

- **WHEN** 任意图片被编码为 Base64
- **THEN** 返回的字符串以 Base64 字符开头，可直接作为 `image` 字段的值提交

#### Scenario: 不支持的图片格式被拒绝

- **WHEN** 传入 GIF 或其他不支持的图片格式
- **THEN** 系统在本地即拒绝并提示格式不受支持，不发起网络请求

### Requirement: 人脸注册接口调用

系统 SHALL 封装 `POST /rest/2.0/face/v3/faceset/user/add`，接受 Base64 图片、`group_id`、`user_id` 与 `user_info`，并返回云端响应。

#### Scenario: 注册请求的成功响应

- **WHEN** 以合法参数调用注册接口且云端返回 `error_code` 为 0
- **THEN** 系统返回成功结果，其中包含云端分配的 `face_token`

#### Scenario: 支持追加与覆盖两种写入方式

- **WHEN** 调用方指定追加方式或覆盖方式
- **THEN** 系统在请求中传入对应的 `action_type` 值，使同一 `user_id` 下的历史人脸被追加保留或被整体替换

#### Scenario: 注册时启用质量与活体控制

- **WHEN** 发起注册请求
- **THEN** 请求中 MUST 携带质量与活体控制参数，以保证入库人脸满足后续检索要求

### Requirement: 人脸检索接口调用

系统 SHALL 封装 `POST /rest/2.0/face/v3/search`，接受 Base64 图片、`group_id_list` 与匹配阈值，返回候选用户列表及其相似度分值。

#### Scenario: 检索命中的响应解析

- **WHEN** 云端返回非空的用户列表
- **THEN** 系统返回其中的 `user_id`、`user_info` 与 `score`，并按分值从高到低排列

#### Scenario: 检索无匹配

- **WHEN** 云端返回错误码 `222207` 表示未找到匹配用户
- **THEN** 系统将其识别为"无匹配结果"而非请求失败，返回空候选列表

#### Scenario: 阈值透传

- **WHEN** 调用方指定了匹配阈值
- **THEN** 系统将该阈值作为 `match_threshold` 传入请求，使低于阈值的候选不被云端返回

### Requirement: 人员删除接口调用

系统 SHALL 封装 `POST /rest/2.0/face/v3/faceset/user/delete`，按 `group_id` 与 `user_id` 删除云端人员。

#### Scenario: 删除成功

- **WHEN** 云端返回 `error_code` 为 0
- **THEN** 系统返回删除成功的结果

#### Scenario: 用户不存在

- **WHEN** 云端返回错误码 `223103` 表示用户不存在
- **THEN** 系统返回可识别的"用户不存在"结果，供上层决定是否清理本地残留记录

### Requirement: 云端错误码映射为可读提示

系统 SHALL 将百度返回的错误码映射为面向使用者的中文提示，覆盖鉴权、配额、图片质量与网络异常等主要类别。

#### Scenario: 图片中未检测到人脸

- **WHEN** 云端返回 `222202` 或 `222203`
- **THEN** 提示使用者照片中未检测到清晰人脸，建议重新采集

#### Scenario: 照片质量不合格

- **WHEN** 云端返回 `223113`、`223114`、`223115`、`223116`、`223120` 或 `223121`-`223129` 之一
- **THEN** 提示使用者对应的具体原因（遮挡、模糊、光照不足、人脸不完整、角度不正或活体未通过）

#### Scenario: 配额或频率超限

- **WHEN** 云端返回 `17`、`18` 或 `19`
- **THEN** 提示使用者接口配额或调用频率已达上限，并说明需等待或提升额度

#### Scenario: 网络异常

- **WHEN** 请求因超时或连接失败未能取得响应
- **THEN** 系统返回明确的网络错误提示，且不将网络错误与业务错误混为一谈

### Requirement: 请求超时与统一会话

系统 SHALL 为所有 HTTP 请求设置连接与读取超时，并复用同一个 HTTP 会话以提升连续调用的效率。

#### Scenario: 请求超时被捕获

- **WHEN** 百度接口在超时时间内未响应
- **THEN** 系统中断该请求，向上层返回网络超时错误，且不使程序崩溃或界面卡死
