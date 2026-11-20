# 仇子睿 · Zirui Qiu

**AI Agent 开发工程师｜大模型应用与 RAG**

[作品集与联系 · ziruiqiu.com](https://ziruiqiu.com/zh-CN/#contact) · [GitHub · Pocket99](https://github.com/Pocket99) · [下载 PDF](./resume.pdf)

在群核科技开发 AIHom 室内设计 Agent 和自然语言户型搜索服务。工作覆盖多 Agent 编排、家具向量检索、MCP 工具接入和模型推理配置。独立上线过面向玩家的对话产品，也为电商运营开发过可读写真实商品的 MCP 服务。

## 专业技能

- **Agent 开发**　Java / Spring AI Alibaba、Python / LangGraph、ReAct、MCP、Function Calling、JSON Schema 结构化输出。
- **检索与调优**　多模态 Embedding、Milvus 向量检索与加权排序、Elasticsearch 条件检索、提示词对照评测、推理参数配置。
- **后端工程**　Spring Boot、FastAPI、Redis Streams、SQL、WebSocket / SSE；工具调用追踪、异步任务、幂等写入与故障恢复。

## 工作经历｜群核科技（酷家乐 / Coohom）

AI 全栈开发工程师 · 2025.08 入职 · 预计 2027.01 结束

### AIHom｜从户型图到可编辑的 3D 设计

Java · Spring AI Alibaba · ReAct · MCP · Milvus · Redis Streams · [官方产品说明](https://www.coohom.com/helpcenter/aihom-design-with-aihom)

设计师上传户型、指定风格后，可以生成带家具的 3D 方案，再通过对话局部换材质或调整布置。我负责 Agent 工作流、检索选品和工具执行链路。

- **多 Agent 编排与 MCP。** 用 LoopAgent 驱动 ReAct 主 Agent，把子 Agent 注册为工具。户型解析、家具匹配和渲染中顺序已知的步骤由程序直接衔接。需要当前 3D 场景的工具通过 WebSocket 发给设计器，例如替换材质、截取场景图；结果回到同一轮对话，供 Agent 决定下一步。
- **软装 RAG 与检索调参。** 接入支持图文 Embedding 的商品检索服务。软装布局将房间风格和家具描述编码为向量，在 Milvus 中按类目、尺寸召回真实商品，再按可配置的商品优先级加权排序。分别配置尺寸容差与排序权重。没有候选时放宽尺寸重查；摆放碰墙时先调整位置，再从同一批候选中换款。
- **跨会话记忆。** 为“这次不要深色沙发”和“以后都不要深色沙发”设计不同处理路径。先按语言筛出可能的偏好表达，经 Redis Streams 异步交给模型判断适用范围，只把长期偏好写入用户记忆，在后续会话中注入上下文。
- **推理参数与故障诊断。** 按 Agent 配置模型、采样温度和最大输出 token，为路由决策指定严格 JSON Schema。排查长任务提前结束时，发现工具虽已返回，执行图却在第 30 步截断。补上最终答复校验，用 35 节点用例验证上限由 30 调至 50 后可正常结束。调整版本通过 16 项定向回归。

### 户型搜索 Agent｜自然语言检索与候选推荐

Python · LangGraph · FastAPI · MCP · Elasticsearch

- **意图理解与工具调用。** 用 LangGraph 把用户描述转成卧室数、面积、地区等结构化条件。信息不足时追问；条件足够时调用 MCP 检索户型库，评估候选并通过 SSE 返回方案。联调环境完成逾 **1.3 万条**户型索引同步和搜索接口验证。
- **空结果处理。** 保留用户的初始条件，优先去掉次要筛选项，再由模型改写描述并重新搜索。回复区分精确匹配和放宽条件后的候选，并为重查设置次数上限，避免反复执行同一查询。

## 个人项目与开源实践

### 咪咪咪｜带长期记忆的角色对话 Agent

独立开发 · 2026.08 起 · Python / DeepSeek / Rust / SQLite · [产品官网](https://mimimi.ziruiqiu.com/)

- **提示词调优。** 保留玩家历史、授权记忆与动作权限，将完整 JSON Schema 中回复所需的字段编译成紧凑说明，用往返测试核对约束。在 3 个合成场景使用同一分词器离线测量，输入 token 减少 **36.4%–39.1%**；校园场景从 8,461 降至 5,153。
- **模型行为评估。** 设计 16 个角色互动场景检查两种对话协议，从中选 5 个用真实模型对比新旧提示词。针对模型虚构玩家动作、忽略角色体力等问题修改提示词，再回填模型自己的上一轮回答，检查它能否延续对话。
- **记忆与计费。** 玩家可确认、编辑和删除长期记忆；写回前核对记忆版本，防止迟到的模型结果恢复已删内容。将玩家点数与供应商 token 成本分别记账，按操作 ID 去重，避免重试时重复调用和扣点。

### YCH-YOYO｜电商运营 MCP 服务

平台全栈负责人 · 2026.10 上线 · Python / Flask / Streamable HTTP · [产品官网](https://ych-yoyo.com/)

- 将销售统计、订单查询、商品维护和图片管理封装为 **9 个 MCP 工具**，按凭据权限开放，并用官方 Python SDK 在线验证工具发现与业务读取。更新商品时校验确认标记和版本，同一操作重试可复用结果，避免覆盖他人修改或重复创建商品。

### Jarvis-AI｜Coding Agent 会话服务

开源项目个人扩展 · 2026.09 · FastAPI / WebSocket · [本人代码与测试](https://github.com/Pocket99/Jarvis-AI/commit/6932adb09e1f09d0fa129453cc42d0c9babb327f)

- 让命令行与网页接续同一会话，支持逐轮切换模型、推送工具执行事件。终端命令等待用户批准，断线则拒绝待批操作，失败轮次不写入历史。编写 10 项自动化测试覆盖审批、会话恢复和并发执行等行为。

## 早期经历与教育

**Think Surgical｜软件工程实习生** · 蒙特利尔 · 2024.04–2025.05。使用 FastAPI、SQLite 和 React 开发医疗软件，以 Playwright 验证用户流程，通过 Docker 交付。

**思必驰 AISpeech｜研发实习生** · 苏州 · 2021.04–2021.08。在 Linux 下用 C/C++ 将 RNN-T 语音识别模型与规则对话引擎接入智能家居和移动应用，参与模型微调与性能验证。

**康考迪亚大学（Concordia University）** · 计算机科学硕士，2022–2024 · 计算机工程学士，2017–2022。

**第一作者论文 2 篇。** 通过对比预训练与分阶段多任务训练联合预测胸片诊断结果和医生注视区域，实验中诊断 AUC 为 0.93、注视预测相关系数为 0.58（Medical Physics，2025）。另研究了气胸识别中 Grad-CAM 热图在不同网络结构上的可靠性（MLMI，2023）。[多任务学习论文](https://pubmed.ncbi.nlm.nih.gov/40665596/) · [Grad-CAM 论文](https://arxiv.org/abs/2308.15172)

<!-- resume:end -->

编辑本页后，运行[生成脚本](./scripts/build_resume.py)即可更新 [HTML](./resume.html) 和 [PDF](./resume.pdf)。[全栈项目长版](https://github.com/Pocket99/ai-product-engineer-resume/blob/ddb91a3f078238964ecc431916591f580054fa29/README.md)和[投递材料说明](./MARKET-AND-SELECTION.md)用于后续调整。
