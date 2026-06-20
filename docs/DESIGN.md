# Aivo-v2 数字人智能体 — 架构设计文档

> 课程设计：构建一个能够实时交互、智能规划完成任务的数字机器人。
> 具备：人形象、表情控制、口型同步、基本动作、工具调用、工作流规划。

---

## 一、总体架构：端云协同

采用 **「云端强算力处理 + 本地轻量级展示」** 的端云分离架构。

```
┌─────────────────────────────┐         ┌──────────────────────────────────────┐
│         Mac（本地客户端）        │         │            H20 DSW（云端后端）            │
│                             │         │                                      │
│  麦克风录音 ──┐                │         │   ┌────────────────────────────────┐  │
│             │  POST /chat   │  HTTP   │   │  FastAPI 统一入口                 │  │
│  摄像头(可选) ─┼──────────────┼────────►│   └──┬──────┬──────┬──────┬────────┘  │
│             │   (音频/文本)   │         │      │      │      │      │           │
│  视频/音频播放 ◄┘               │ WebSocket│   ASR    Agent   TTS  数字人驱动      │
│  (浏览器 / PyQt)              │◄────────│  Whisper  Dify   API  MuseTalk        │
│                             │ (视频流) │           (大脑)        /SadTalker      │
└─────────────────────────────┘         └──────────────────────────────────────┘
                                              LLM 用 API（Claude/Qwen/DeepSeek）
                                              显存专供：数字人驱动 + ASR + 自定义TTS
```

### 设计原则：显存预算分配

H20 拥有 96GB 显存，但需精打细算。核心原则是 **「有 API 的走 API，没 API 的才上 DSW」**：

| 模块 | 部署位置 | 理由 |
|------|---------|------|
| LLM 推理（大脑） | **API** | 工具调用/JSON 输出稳定，0 显存占用，省下显存给渲染 |
| 数字人面部驱动 | **DSW** | 无现成 API，必须本地跑，吃显存大头 |
| ASR 语音识别 | **DSW / API** | Whisper 本地或用云 API |
| TTS 语音合成 | **API / DSW** | 通用音色用 API；自定义音色用 GPT-SoVITS 跑 DSW |
| Agent 工作流编排 | **DSW (Dify)** | 可视化编排，答辩演示直观 |

> **关键决策：** LLM 大脑用 API 而非自托管开源模型（如 Hermes/Qwen 本地版）。
> 原因：① 数字人驱动 + ASR + TTS 已占用大量显存；② 开源小模型在工具调用、
> 结构化 JSON 输出上稳定性较差，而这正是本项目的核心；③ 把宝贵显存留给
> 「只能本地跑」的音视频算法。

---

## 二、技术选型

### 2.1 数字人驱动

**方案 A — 2D 驱动（推荐，快速落地）**
- [Linly-Talker](https://github.com/Kedreamix/Linly-Talker)：已集成 ASR + LLM + 数字人 + TTS 全链路，DSW 一键部署
- [MuseTalk](https://github.com/TMElyralab/MuseTalk)：阿里出品，实时口型驱动，效果优于 Wav2Lip
- [SadTalker](https://github.com/OpenTalker/SadTalker)：支持 `expression_scale` 参数控制表情强度
- 优点：H20 上接近实时；缺点：仅头部动作，无肢体

**方案 B — 3D 虚拟形象（效果好，略复杂）**
- [three-vrm](https://github.com/pixiv/three-vrm)：前端渲染 VRM 模型，支持骨骼动作 + 表情 blendshape
- MuseTalk 驱动口型 + VRM 控制表情/动作

> 课设建议：先用 **方案 A（Linly-Talker / MuseTalk）** 跑通全链路，
> 有余力再升级到方案 B 加肢体动作。

### 2.2 Agent 工作流：Dify

选 Dify 的原因：
- 可视化编排工作流，答辩演示直观
- 原生支持工具调用（HTTP、Python 代码块、数据库查询）
- 提供 REST API，前端可直接调用
- 支持 Docker 一键部署

**计划接入的工具（demo 够用）：**
- 天气查询（和风天气 API）
- 网络搜索（Tavily / Serper）
- 日历 / 提醒（本地 Python 脚本）
- 数据库查询（SQLite）

### 2.3 网络通信

**方案 A — SSH 端口转发（开发调试用，最简单）**
```bash
ssh -L 7860:localhost:7860 root@<DSW_IP> -p <SSH端口>
# Mac 浏览器访问 http://localhost:7860
```

**方案 B — WebSocket / WebRTC（进阶，自定义前端）**
- Mac 通过 WebSocket 向 DSW 发送语音片段
- DSW 处理后实时推回视频帧（二进制/Base64）和音频流

---

## 三、核心设计：动作指令协议

让 LLM 输出 **结构化 JSON**，而非纯文本，从而驱动数字人的表情和动作：

```json
{
  "speech": "好的，我已经帮您查到了明天的天气",
  "emotion": "happy",
  "action": "nod",
  "tool_result": { "weather": "晴，25°C" }
}
```

前端根据 `emotion` 和 `action` 字段切换表情图层 / 播放动作片段。
这一层是「智能体能控制数字人行为」的关键，也是课设的工程亮点。

---

## 四、数据流：一次完整交互

```
1. 用户在 Mac 按键说话         → 麦克风录音
2. 音频 POST 到 DSW           → FastAPI /chat
3. ASR 转文本                 → Whisper
4. 文本进入 Agent             → Dify Workflow
   ├─ 意图识别（闲聊 / 任务）
   ├─ 工具调用（查天气 / 搜索 / 数据库）
   └─ 生成结构化回复 JSON（speech + emotion + action）
5. speech 文本 → TTS          → 音频
6. 音频 → 数字人驱动            → MuseTalk/SadTalker 生成视频
7. 视频流 + 情感/动作指令       → WebSocket 推回 Mac
8. Mac 播放视频 + 渲染表情动作
```

---

## 五、项目目录结构（规划）

```
Aivo-v2/
├── docs/                    # 设计文档
│   └── DESIGN.md
├── dsw/                     # 云端后端（部署在 H20 DSW）
│   ├── api/                 # FastAPI 统一入口
│   ├── asr/                 # 语音识别封装
│   ├── tts/                 # 语音合成封装
│   ├── avatar/              # 数字人驱动封装（MuseTalk/SadTalker）
│   └── agent/               # Dify 工作流配置 / Agent 编排
├── mac-client/              # 本地前端（Mac）
│   ├── web/                 # 网页客户端（录音 + 播放）
│   └── desktop/             # 可选：PyQt 桌面客户端
└── README.md
```

---

## 六、实施路线图

| 阶段 | 任务 | 产出 |
|------|------|------|
| 第 1-2 天 | DSW 部署 Linly-Talker，SSH 转发到 Mac，跑通完整链路 | 能对话的数字人 WebUI |
| 第 3-4 天 | 搭 Dify，设计工作流，接入 ≥2 个工具 | 可工具调用的 Agent |
| 第 5-6 天 | FastAPI 把数字人驱动 + Dify 串成统一接口 | 统一后端 API |
| 第 7 天 | 写 Mac 前端（Gradio / 网页） | 可交互前端 |
| 收尾 | 加情感 / 动作控制层，打磨 demo | 完整 demo + 答辩材料 |

---

## 七、课设答辩亮点

1. **端云解耦架构** — 前后端分离，符合工程最佳实践
2. **显存资源的合理调度** — API 与本地算法的分工决策有理有据
3. **动作指令协议** — 智能体不仅会说话，还能控制数字人的表情与动作
4. **工作流规划展示** — 演示「任务分解」场景（如"安排明天的工作计划" → 查日历 + 查天气 + 生成计划 + 数字人播报）

---

## 八、待决策项

- [ ] 数字人方案：2D（Linly-Talker/MuseTalk）还是 3D（VRM）？
- [ ] TTS 音色：通用 API 音色还是自定义克隆音色（GPT-SoVITS）？
- [ ] 前端形态：复用开源 WebUI 还是自写控制台？
- [ ] LLM API 提供方：Claude / Qwen / DeepSeek？
