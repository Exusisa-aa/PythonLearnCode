# 人脸识别系统（百度智能云）

一个基于百度智能云人脸识别 API 的桌面程序，实现**人员注册**、**单人识别**与**陌生人判断**，并带有人脸库管理界面。

技术栈：Python 3.10+ / Tkinter / OpenCV / SQLite / 百度智能云人脸识别 API。

---

## 功能

| 功能 | 说明 |
|---|---|
| 人员注册 | 输入姓名，通过摄像头抓拍或选择图片，人脸存入百度云端人脸库 |
| 单人识别 | 对摄像头画面或图片执行 1:N 检索，输出最相似人员姓名与相似度 |
| 陌生人判断 | 相似度低于阈值时输出"陌生人"，不强行匹配 |
| 人脸库管理 | 查看已注册人员列表与明细、删除人员（云端与本地同步） |
| 简单界面 | 三个页签的 Tkinter 窗口，耗时操作不冻结界面 |

---

## 安装

```bash
cd opencv/last
pip install -r requirements.txt
```

依赖：`opencv-python`、`requests`、`python-dotenv`、`Pillow`。
`tkinter` 与 `sqlite3` 为 Python 标准库，通常已随 Python 安装。

> Windows 下若提示缺少 `tkinter`，请重新运行 Python 安装程序并勾选 **tcl/tk and IDLE** 组件。

---

## 获取百度 AK / SK

1. 登录 [百度智能云控制台](https://console.bce.baidu.com/)，完成**个人或企业实名认证**（未实名无法使用人脸识别接口）。
2. 进入 **人工智能 → 人脸识别 → 概览**，点击「创建应用」。
3. 应用创建后，在「应用列表」中查看该应用的 **API Key** 与 **Secret Key**。
4. 免费测试资源需在控制台另行领取。

---

## 配置

```bash
cp .env.example .env
```

编辑 `.env`：

```ini
BAIDU_API_KEY=你的API Key
BAIDU_SECRET_KEY=你的Secret Key
FACE_GROUP_ID=face_recognition
MATCH_THRESHOLD=80
```

| 配置项 | 必填 | 说明 |
|---|---|---|
| `BAIDU_API_KEY` | 是 | 控制台应用的 API Key |
| `BAIDU_SECRET_KEY` | 是 | 控制台应用的 Secret Key |
| `FACE_GROUP_ID` | 否 | 人脸库用户组名，仅限数字/字母/下划线，≤48 字节，默认 `face_recognition` |
| `MATCH_THRESHOLD` | 否 | 相似度判定阈值（0~100），默认 80（百度官方推荐值） |
| `QUALITY_CONTROL` | 否 | 注册时的质量控制等级 `NONE`/`LOW`/`NORMAL`/`HIGH`，默认 `NORMAL` |
| `LIVENESS_CONTROL` | 否 | 注册时的活体检测等级 `NONE`/`LOW`/`NORMAL`/`HIGH`，默认 `NORMAL` |

> **注册时被提示"活体检测未通过"，怎么办？**
> 默认的 `LIVENESS_CONTROL=NORMAL` 会拒绝二次翻拍的照片（错误码 `223120`）。
> 如果你主要用**已有的图片文件**注册而不是现场拍摄，可能会被误拒——把
> `LIVENESS_CONTROL` 改成 `LOW` 或 `NONE` 即可。用摄像头现场拍摄时请保持 `NORMAL`。

> `.env` 已被 `.gitignore` 排除，**不要**把密钥提交到仓库。

---

## 运行

```bash
python app.py
```

- **人员注册**：输入姓名 → 抓拍或选择图片 → 点击注册。同名重复注册会为该人员**追加**一张人脸（同一人最多 20 张），可提升后续识别命中率。
- **单人识别**：抓拍或选择图片 → 点击识别。结果显示姓名与相似度，低于阈值则显示"陌生人"。
- **人脸库管理**：查看已注册人员，选中可在右侧看明细，点击删除可移除该人员。

各模块也可单独运行自测：

```bash
python core/database.py     # 数据库增删改查自测
python core/baidu_client.py # 百度接口全链路冒烟测试（需先配好 .env）
```

---

## 项目结构

```
opencv/last/
├── app.py                    # 程序入口
├── config.py                 # 配置加载
├── core/
│   ├── baidu_client.py       # 百度人脸 API 封装
│   ├── database.py           # SQLite 本地档案
│   ├── camera.py             # 摄像头采集线程
│   └── errors.py             # 云端错误码 → 中文提示
├── ui/
│   ├── main_window.py        # 主窗口与异步辅助
│   ├── register_tab.py       # 人员注册
│   ├── recognize_tab.py      # 单人识别
│   └── faceset_tab.py        # 人脸库管理
├── data/                     # 运行时生成，已 gitignore
│   ├── faces.db              # 本地档案数据库
│   └── faces/                # 注册照片
├── .env                      # 你的密钥（不提交）
└── .env.example
```

---

## 相关文档

| 文档 | 内容 |
|---|---|
| [技术栈报告.md](技术栈报告.md) | 完整技术栈清单、逐文件代码详解、关键技术专题、开发中实测发现的 6 个真实缺陷 |
| [openspec/changes/baidu-face-recognition/](openspec/changes/baidu-face-recognition/) | 需求规格（5 个能力 / 29 条需求 / 84 个场景）、设计文档、任务清单 |

## 设计说明

**人脸特征存放在百度云端。** 百度在线 API **不返回原始人脸特征向量**，只能返回 `face_token` 与相似度分值，特征比对在百度侧完成。因此"提取并保存人脸特征"的落地形态是：把人脸注册进云端人脸库，本地 SQLite 仅保存姓名、`user_id`、`face_token`、照片路径等档案信息。

**中文姓名的处理。** 百度的 `user_id` 只允许数字、字母、下划线且 ≤48 字节，中文不能直接用。程序用 `"u" + md5(姓名)[:16]` 派生 `user_id`，姓名本身通过 `user_info` 字段承载。

---

## 注意事项与限制

- **配额限制**：免费额度约为 **1 QPS、1000 次/月**（以控制台实际为准）。程序已做优化——注册时不额外调用人脸检测接口（直接依赖注册接口自带的质量控制），并缓存 `access_token` 减少请求；识别按钮带防重复点击。
- **不要删除控制台中的 appid**：每个人脸库对应一个 appid，删除应用会导致该人脸库**整体失效**，无法再进行任何检索。
- **注册与删除都有同步延迟**：注册后约 **5 秒**才能在检索中生效；删除人员后，百度侧的**检索索引同步可能还要几秒**，期间立即识别仍可能匹配到已删除的人员。两个界面都已在提示中说明这一点。
- **人脸库闲置释放**：人脸库若超过 **1 年**未使用（无入库、搜索等操作），平台会释放相关资源以确保用户信息安全。
- **接口限流**：免费额度仅 1 QPS，客户端已在两次调用间自动保持约 1.05 秒间隔（`core/baidu_client.py` 中的 `MIN_REQUEST_INTERVAL_SECONDS`），避免连点触发错误码 `18`。若已购买更高 QPS 可下调该值。
- **中文路径**：图片读写一律走 `core/images.py`（`imdecode`/`imencode` + `pathlib`），**不要改用 `cv2.imread`/`cv2.imwrite`**——它们在 Windows 上无法处理含中文的路径，且是静默失败。
- **`access_token` 有效期 30 天**：程序会自动获取与刷新，无需手工干预。
- **图像格式**：支持 PNG / JPG / JPEG / BMP，**不支持 GIF**；Base64 编码后需小于 2M，分辨率建议 1920×1080 以下。
- **无摄像头环境**：程序会自动降级为"仅从文件选择图片"，注册与识别仍可用。
- **相似度阈值**：临界情况（如 78~85 分）建议结合实际场景调整 `MATCH_THRESHOLD`；界面会同时显示分值与本轮阈值，便于判断。
