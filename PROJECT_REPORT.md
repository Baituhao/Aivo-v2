# Aivo V6 数字人系统 - 完整项目报告

> **版本**: V6.0 | **最后更新**: 2026-06-21 | **状态**: 生产就绪

---

## 📑 目录

1. [项目概述](#1-项目概述)
2. [系统架构](#2-系统架构)
3. [核心功能](#3-核心功能)
4. [技术实现](#4-技术实现)
5. [模块详解](#5-模块详解)
6. [数据存储](#6-数据存储)
7. [用户界面](#7-用户界面)
8. [API 集成](#8-api-集成)
9. [部署与配置](#9-部署与配置)
10. [性能与成本](#10-性能与成本)
11. [安全与隐私](#11-安全与隐私)
12. [未来规划](#12-未来规划)

---

## 1. 项目概述

### 1.1 项目简介

Aivo V6 是一个基于小米 MiMo API 的智能数字人系统，集成了 **Live2D 数字人渲染**、**多模态交互**、**会话管理**和 **Soul Memory 灵魂记忆系统**，提供自然、流畅的人机对话体验。

### 1.2 核心特性

| 特性 | 说明 |
|------|------|
| 🎀 **Live2D 数字人** | 3D 渲染，3 个模型可切换，语音同步动画 |
| 🎵 **气泡语音** | 音频嵌入对话气泡，自动播放 |
| 🛠️ **工具系统** | 9 种实用工具，自动识别意图调用 |
| 🎤 **8 种音色** | 中英文男女声，情感自动匹配 |
| 📊 **实时统计** | 对话轮次、响应时间、情感分布可视化 |
| 📜 **会话管理** | 持久化存储、多会话切换、历史搜索 |
| 🧠 **Soul Memory** | 人格设定、用户画像、技能管理、偏好设置 |

### 1.3 技术栈

```
前端: Gradio 4.x + HTML/CSS/JavaScript
后端: Python 3.8+
AI 模型: 小米 MiMo (mimo-v2.5-pro)
数字人: Live2D Cubism SDK 4 + PixiJS
音频: Fish Audio TTS + PyAudio
存储: JSON 文件持久化
```

---

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户界面层 (Web UI)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │   对话区域    │  │  Live2D 渲染  │  │  控制面板（统计/管理） │   │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘   │
├─────────┼─────────────────┼──────────────────────┼───────────────┤
│         │           应用逻辑层                    │               │
│  ┌──────▼─────────────────▼──────────────────────▼───────────┐  │
│  │                    Web UI V6 主控制器                       │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌─────────┐ │  │
│  │  │ 会话管理器  │ │ Soul Memory│ │ 统计引擎   │ │ UI 渲染 │ │  │
│  │  └────────────┘ └────────────┘ └────────────┘ └─────────┘ │  │
│  └───────────────────────────┬───────────────────────────────┘  │
├──────────────────────────────┼──────────────────────────────────┤
│                         服务层                                   │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌─────────────┐  │
│  │ LLM Service│ │ TTS Service│ │ ASR Service│ │ Tool Registry│  │
│  │  (对话/推理) │ │  (语音合成) │ │  (语音识别) │ │  (工具注册)  │  │
│  └──────┬─────┘ └──────┬─────┘ └──────┬─────┘ └──────┬──────┘  │
├─────────┼───────────────┼──────────────┼───────────────┼────────┤
│         │           外部服务层          │               │         │
│  ┌──────▼───────────────▼──────────────▼───────────────▼──────┐ │
│  │                    MiMo API (小米)                          │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐  │ │
│  │  │ LLM API  │ │ TTS API  │ │ ASR API  │ │ External APIs │  │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 数据流

```
用户输入（文本/语音）
    │
    ▼
┌─────────────┐     ┌─────────────┐
│ ASR 识别     │────▶│ LLM 推理    │
│ (语音→文本)  │     │ (意图理解)   │
└─────────────┘     └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │ 工具调用     │
                    │ (可选)      │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │ 响应生成     │
                    │ (JSON 格式)  │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌─────────┐  ┌─────────┐  ┌─────────┐
        │ TTS 合成 │  │ UI 更新 │  │ 记忆存储 │
        │ (语音)   │  │ (显示)   │  │ (持久化) │
        └─────────┘  └─────────┘  └─────────┘
```

### 2.3 分层设计

| 层次 | 职责 | 组件 |
|------|------|------|
| **用户界面层** | 交互展示、视觉反馈 | Gradio Web UI、Live2D 渲染 |
| **应用逻辑层** | 业务逻辑、状态管理 | 会话管理、Soul Memory、统计引擎 |
| **服务层** | AI 能力封装 | LLM、TTS、ASR、工具系统 |
| **外部服务层** | 第三方 API | MiMo API、天气 API、搜索 API |

---

## 3. 核心功能

### 3.1 智能对话系统

**功能描述**: 基于 MiMo 大模型的多轮对话，支持上下文记忆和意图识别。

**技术特点**:
- 多轮对话上下文维护（最近 10 轮）
- 结构化 JSON 响应（speech/emotion/action）
- 工具调用自动识别（Function Calling）
- 中英文混合支持

**响应格式**:
```json
{
  "speech": "你好，很高兴见到你！",
  "emotion": "happy",
  "action": "wave"
}
```

### 3.2 Live2D 数字人

**功能描述**: 基于 Cubism SDK 4 的 Live2D 数字人渲染，支持模型切换和语音同步。

**技术实现**:
- PixiJS 渲染引擎
- Cubism 4 Core SDK
- iframe 隔离渲染（绕过 Gradio 沙箱）
- postMessage 通信协议

**支持的模型**:
1. **Shizuku** - 可爱少女风格
2. **Hijiki** - 黑猫风格
3. **Tororo** - 白猫风格

**动画控制**:
- 情感表情切换（happy/sad/neutral/surprised）
- 语音同步嘴型动画
- 点击交互切换模型

### 3.3 语音交互系统

#### TTS 语音合成

**功能描述**: 文本转语音，支持 8 种音色和情感匹配。

**音色列表**:

| 音色 | 性别 | 语言 | 风格描述 |
|------|------|------|----------|
| 冰糖 | 女 | 中文 | 明亮活泼、元气满满 |
| 茉莉 | 女 | 中文 | 温柔平静、知性优雅 |
| 苏打 | 男 | 中文 | 沉稳大气、富有磁性 |
| 白桦 | 男 | 中文 | 清朗阳光、亲和力强 |
| Mia | 女 | 英文 | 温柔甜美 |
| Chloe | 女 | 英文 | 专业清晰 |
| Milo | 男 | 英文 | 沉稳专业 |
| Dean | 男 | 英文 | 亲切友好 |

**情感音色映射**:
```json
{
  "happy": "冰糖/白桦",
  "sad": "茉莉/苏打",
  "neutral": "茉莉/苏打",
  "surprised": "冰糖/白桦"
}
```

#### ASR 语音识别

**功能描述**: 音频转文本，支持麦克风录音和文件上传。

**技术参数**:
- 采样率: 16kHz
- 通道: 单声道
- 格式: WAV
- 语言: 中文/英文

### 3.4 工具系统

**功能描述**: 9 种实用工具，通过 Function Calling 自动识别意图并调用。

| 工具 | 功能 | API 来源 |
|------|------|----------|
| 🌤️ 天气查询 | 实时天气信息 | wttr.in |
| ⏰ 时间日期 | 当前时间日期 | 系统时间 |
| 🔢 计算器 | 数学运算 | Python eval |
| 🔍 网络搜索 | 信息检索 | DuckDuckGo |
| ⏱️ 提醒工具 | 设置提醒事项 | 本地存储 |
| 🌐 翻译工具 | 中英互译 | MyMemory API |
| 📚 维基百科 | 知识查询 | Wikipedia API |
| 📝 笔记工具 | 本地笔记管理 | JSON 存储 |
| 📰 新闻工具 | 获取资讯 | NewsAPI |

**工具注册机制**:
```python
# src/tools/__init__.py
tool_registry.register(WeatherTool())
tool_registry.register(DateTimeTool())
# ... 更多工具
```

**工具定义示例**:
```json
{
  "type": "function",
  "function": {
    "name": "get_weather",
    "description": "查询指定城市的天气信息",
    "parameters": {
      "type": "object",
      "properties": {
        "city": {
          "type": "string",
          "description": "城市名称"
        }
      },
      "required": ["city"]
    }
  }
}
```

### 3.5 会话管理系统

**功能描述**: 持久化对话历史，支持多会话切换和跨会话搜索。

**核心功能**:
- ✅ 自动保存会话到 `sessions/` 目录
- ✅ 启动时自动加载最近会话
- ✅ 新建会话、加载历史会话
- ✅ 对话框左上角快速切换（显示第一条消息和会话 ID）
- ✅ 会话选择器显示格式: `💬 "第一条消息" (对话数条) - 时间 [ID:会话ID]`
- ✅ 导出会话为 JSON 文件
- ✅ **跨会话搜索** - 在所有历史会话中搜索关键词，显示来源会话

**会话加载机制**:
1. 从会话文件读取 JSON 数据
2. 恢复会话元数据（ID、时间、统计）
3. 重建 LLM 对话历史记忆（用于上下文理解）
4. 重建显示历史（用于界面展示）
5. 同步更新两个会话选择器

**会话数据结构**:
```json
{
  "session_id": "20260621_143000",
  "created_at": "2026-06-21 14:30:00",
  "last_updated": "2026-06-21 15:45:00",
  "session_start_time": 1718952600.0,
  "response_times": [1.2, 0.8, 1.5],
  "stats": {
    "conversation_count": 10,
    "tool_calls": 3,
    "emotion_changes": 5,
    "total_words": 500
  },
  "conversation_history": [
    {
      "timestamp": "2026-06-21 14:30:05",
      "user": "你好",
      "assistant": "你好！很高兴见到你！",
      "emotion": "happy",
      "response_time": 1.2
    }
  ]
}
```

### 3.6 Soul Memory 灵魂记忆系统

**功能描述**: 持久化存储 AI 人格、用户画像、技能和偏好设置。

#### 人格设定 (Personality)

```json
{
  "name": "Aivo",
  "role": "AI数字人助手",
  "traits": ["友好热情", "专业可靠", "善解人意", "积极向上"],
  "speaking_style": "温暖亲切，乐于助人",
  "created_at": "2026-06-21 10:00:00",
  "last_updated": "2026-06-21 15:30:00"
}
```

#### 用户画像 (User Profile)

```json
{
  "name": "小明",
  "interests": ["编程", "AI技术", "音乐"],
  "habits": ["晚上工作", "喜欢语音交互"],
  "background": "软件工程师",
  "interaction_history": {
    "first_interaction": "2026-06-20 10:00:00",
    "total_interactions": 50,
    "favorite_topics": ["天气", "技术"]
  }
}
```

#### 技能系统 (Skills)

```json
{
  "knowledge_domains": [
    {"name": "通用对话", "level": "expert", "enabled": true},
    {"name": "天气查询", "level": "expert", "enabled": true},
    {"name": "信息搜索", "level": "expert", "enabled": true}
  ],
  "custom_skills": [
    {"name": "Python编程", "level": "expert", "enabled": true},
    {"name": "机器学习", "level": "intermediate", "enabled": true}
  ]
}
```

#### 偏好设置 (Preferences)

```json
{
  "language": "中文",
  "voice": "冰糖",
  "response_style": "详细",
  "emoji_usage": "适中",
  "humor_level": "适中",
  "formality": "友好"
}
```

### 3.7 实时统计面板

**功能描述**: 实时显示对话统计数据和情感分布。

**统计指标**:
- 💬 对话轮次
- ⚡ 平均响应时间
- 🎭 情感切换次数
- 📝 总字数
- ⏱️ 会话时长
- 🔧 工具调用次数

**可视化**:
- 情感分布进度条
- 渐变卡片设计
- 实时数据刷新

---

## 4. 技术实现

### 4.1 LLM 服务实现

**文件**: `src/llm_service_v2.py`

**核心类**: `LLMServiceWithTools`

**关键方法**:
```python
class LLMServiceWithTools:
    def chat(self, user_message: str, use_tools: bool = True) -> Dict:
        """发送消息并获取回复（支持工具调用）"""

    def clear_history(self):
        """清空对话历史"""

    def add_to_history(self, role: str, content: str):
        """添加消息到对话历史"""

    def set_history(self, history: List[Dict]):
        """设置对话历史（用于会话恢复）"""
```

**工具调用流程**:
```
1. 用户消息 → LLM 第一次调用
2. 检测到 tool_calls → 执行工具
3. 工具结果 → LLM 第二次调用
4. 生成最终回复（JSON 格式）
```

### 4.2 TTS 服务实现

**文件**: `src/tts_service.py`

**核心类**: `TTSService`

**合成流程**:
```python
def synthesize(self, text: str, emotion: str, voice: str) -> str:
    # 1. 自动选择音色（如果未指定）
    if not voice:
        voice = self.voice_manager.select_voice(emotion)

    # 2. 添加情感标签
    text_with_emotion = self.voice_manager.add_emotion_tag(text, emotion)

    # 3. 调用 TTS API
    completion = self.client.chat.completions.create(
        model="mimo-v2.5-tts",
        modalities=["text", "audio"],
        audio={"voice": voice, "format": "wav"},
        messages=[...]
    )

    # 4. 解码并保存音频
    audio_base64 = completion.choices[0].message.audio.data
    # ...
```

### 4.3 ASR 服务实现

**文件**: `src/asr_service.py`

**核心类**: `ASRService`

**识别流程**:
```python
def transcribe(self, audio_path: str, language: str = "zh") -> str:
    # 1. 读取音频文件
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()

    # 2. 转为 base64
    audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

    # 3. 调用 ASR API
    completion = self.client.chat.completions.create(
        model="mimo-v2.5-asr",
        messages=[{
            "role": "user",
            "content": [{
                "type": "input_audio",
                "input_audio": {"data": f"data:audio/wav;base64,{audio_base64}"}
            }]
        }]
    )

    # 4. 返回识别结果
    return completion.choices[0].message.content
```

### 4.4 Soul Memory 实现

**文件**: `src/soul_memory.py`

**核心类**: `SoulMemory`

**设计模式**:
- 单例模式：全局唯一实例
- 持久化模式：JSON 文件存储
- 自动初始化：首次使用创建默认配置

**关键方法**:
```python
class SoulMemory:
    def update_personality(self, **kwargs):
        """更新人格设定"""

    def update_user_profile(self, **kwargs):
        """更新用户画像"""

    def add_skill(self, name: str, level: str, enabled: bool):
        """添加技能"""

    def update_preferences(self, **kwargs):
        """更新偏好设置"""

    def export_all(self, export_path: Path):
        """导出所有记忆"""

    def import_all(self, import_path: Path):
        """导入所有记忆"""
```

### 4.5 工具系统实现

**文件**: `src/tools/base.py`

**核心类**:
- `BaseTool`: 工具基类，定义通用接口
- `ToolRegistry`: 工具注册表，管理所有工具

**工具基类**:
```python
class BaseTool:
    @property
    def name(self) -> str:
        """工具名称"""

    @property
    def description(self) -> str:
        """工具描述"""

    @property
    def parameters(self) -> Dict:
        """参数定义"""

    def execute(self, **kwargs) -> str:
        """执行工具"""
```

**工具注册**:
```python
class ToolRegistry:
    def register(self, tool: BaseTool):
        """注册工具"""

    def get_all_definitions(self) -> List[Dict]:
        """获取所有工具定义（用于 Function Calling）"""

    def execute_tool(self, tool_name: str, **kwargs) -> str:
        """执行指定工具"""
```

---

## 5. 模块详解

### 5.1 文件结构

```
Aivo-v2/
├── src/                          # 源代码目录
│   ├── web_ui_v6.py              # 主界面（核心）
│   ├── soul_memory.py            # Soul Memory 系统
│   ├── llm_service_v2.py         # LLM 服务
│   ├── tts_service.py            # TTS 服务
│   ├── asr_service.py            # ASR 服务
│   ├── voice_manager.py          # 音色管理
│   ├── tools/                    # 工具系统
│   │   ├── __init__.py           # 工具注册
│   │   ├── base.py               # 工具基类
│   │   ├── weather.py            # 天气查询
│   │   ├── utils.py              # 时间、计算器
│   │   ├── search.py             # 网络搜索
│   │   ├── reminder_tool.py      # 提醒工具
│   │   ├── translation_tool.py   # 翻译工具
│   │   ├── wiki_tool.py          # 维基百科
│   │   ├── note_tool.py          # 笔记工具
│   │   └── news_tool.py          # 新闻工具
│   └── static/                   # 静态资源
│       ├── live2d_pixi.html      # Live2D 渲染页面
│       ├── live2dcubismcore.min.js
│       └── pixi-live2d-display.min.js
├── memory/                       # Soul Memory 存储
│   ├── personality.json
│   ├── user_profile.json
│   ├── skills.json
│   └── preferences.json
├── sessions/                     # 会话历史存储
│   └── session_*.json
├── config/                       # 配置文件
│   └── voice_settings.json
├── output/                       # 输出目录
│   └── audio/                    # TTS 生成的音频
├── tests/                        # 测试脚本
├── docs/                         # 文档目录
├── requirements.txt              # Python 依赖
└── .gitignore                    # Git 配置
```

### 5.2 模块依赖关系

```
web_ui_v6.py
    ├── llm_service_v2.py
    │   └── tools/
    ├── tts_service.py
    │   └── voice_manager.py
    ├── asr_service.py
    ├── soul_memory.py
    └── static/
        └── live2d_pixi.html
```

### 5.3 关键类图

```
┌─────────────────────────────────────────────────────────────┐
│                    AivoWebUIV6 (主控制器)                     │
├─────────────────────────────────────────────────────────────┤
│ - llm: LLMServiceWithTools                                  │
│ - tts: TTSService                                           │
│ - asr: ASRService                                           │
│ - soul_memory: SoulMemory                                   │
│ - current_session_id: str                                   │
│ - stats: Dict                                               │
│ - conversation_history: List                                │
├─────────────────────────────────────────────────────────────┤
│ + chat(message, history, voice)                             │
│ + process_voice(audio_file, history, voice)                 │
│ + new_session()                                             │
│ + load_session(session_id)                                  │
│ + export_history()                                          │
│ + search_history(keyword)                                   │
│ + build_interface()                                         │
└─────────────────────────────────────────────────────────────┘
         │                │                │
         ▼                ▼                ▼
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│LLMServiceWithTools│ │  TTSService    │ │  ASRService    │
├────────────────┤ ├────────────────┤ ├────────────────┤
│- client: OpenAI│ │- client: OpenAI│ │- client: OpenAI│
│- model: str    │ │- voice_manager │ │- output_dir    │
│- history: List │ │- output_dir    │ ├────────────────┤
├────────────────┤ ├────────────────┤ │+ record_audio()│
│+ chat()        │ │+ synthesize()  │ │+ transcribe()  │
│+ clear_history()│ │+ play_audio()  │ └────────────────┘
│+ set_history() │ └────────────────┘
└────────────────┘
         │
         ▼
┌────────────────┐
│  ToolRegistry  │
├────────────────┤
│- tools: Dict   │
├────────────────┤
│+ register()    │
│+ execute_tool()│
│+ get_definitions()│
└────────────────┘
```

---

## 6. 数据存储

### 6.1 存储架构

```
Aivo-v2/
├── memory/                       # Soul Memory 存储
│   ├── personality.json          # 人格设定
│   ├── user_profile.json         # 用户画像
│   ├── skills.json               # 技能列表
│   └── preferences.json          # 偏好设置
├── sessions/                     # 会话历史存储
│   ├── session_20260621_085734.json
│   └── session_20260621_090023.json
├── output/                       # 输出文件
│   ├── audio/                    # TTS 生成的音频
│   ├── notes.json                # 笔记存储
│   └── reminders.json            # 提醒存储
└── config/                       # 配置文件
    └── voice_settings.json       # 音色配置
```

### 6.2 数据持久化策略

| 数据类型 | 存储位置 | 更新频率 | 备份策略 |
|----------|----------|----------|----------|
| 人格设定 | memory/personality.json | 手动更新 | 导出备份 |
| 用户画像 | memory/user_profile.json | 手动更新 | 导出备份 |
| 技能列表 | memory/skills.json | 手动更新 | 导出备份 |
| 偏好设置 | memory/preferences.json | 手动更新 | 导出备份 |
| 会话历史 | sessions/session_*.json | 每次对话 | 自动保存 |
| 音频文件 | output/audio/ | 每次 TTS | 可清理 |

### 6.3 数据安全

- **本地存储**: 所有数据存储在本地，不上传云端
- **Git 保护**: 敏感目录已加入 `.gitignore`
- **导入导出**: 支持备份和迁移
- **自动保存**: 会话数据实时持久化

---

## 7. 用户界面

### 7.1 界面布局

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Aivo 数字人 V6 顶部横幅                        │
│      ✨ Live2D交互 · 🎵 气泡语音 · 🛠️ 9种工具 · 🎤 8种音色 · 🧠 Soul  │
│                         ⭐ GitHub 仓库                               │
├─────────────────────────────────────┬───────────────────────────────┤
│                                     │                               │
│   💬 对话历史 - 切换会话             │    💫 Live2D 数字人            │
│   ┌─────────────────────────────┐   │    ┌───────────────────────┐  │
│   │ 💬 "你好" (5条) - 14:30 [ID:xxx] │ │                       │  │
│   └─────────────────────────────┘   │      [Live2D 渲染]       │  │
│                                     │                       │  │
│   ┌─────────────────────────────┐   │    └───────────────────────┘  │
│   │                             │   │                               │
│   │       对话内容区域           │   │    📊 实时统计面板             │
│   │                             │   │    ┌───────────────────────┐  │
│   │   💬 用户消息               │   │    │ 💬 对话轮次 │ ⚡ 响应  │  │
│   │   🤖 AI 回复 (带音频)        │   │    │ 🎭 情感切换 │ 📝 字数  │  │
│   │                             │   │    └───────────────────────┘  │
│   └─────────────────────────────┘   │                               │
│                                     │                               │
│   ┌─────────────────────────────┐   │                               │
│   │ 💬 输入消息...    [📤 发送]  │   │                               │
│   └─────────────────────────────┘   │                               │
│                                     │                               │
│   🎤 语音输入                        │                               │
│   ┌─────────────────────────────┐   │                               │
│   │ [录音] [上传]  [🎙️ 识别]    │   │                               │
│   └─────────────────────────────┘   │                               │
│                                     │                               │
│   ┌─────┬─────┬─────┬─────┬─────┐  │                               │
│   │ 📜  │ 🎵  │ 💡  │ 🛠️  │ 🧠  │  │                               │
│   │会话 │音色 │示例 │工具 │记忆 │  │                               │
│   │管理 │选择 │    │    │    │  │                               │
│   └─────┴─────┴─────┴─────┴─────┘  │                               │
│                                     │                               │
├─────────────────────────────────────┴───────────────────────────────┤
│                         🚀 技术实现                                  │
│   ┌─────────────────────────────────────────────────────────────┐  │
│   │  📍 实现路径: 需求分析 → 架构设计 → 核心开发 → 集成测试 → 部署  │  │
│   └─────────────────────────────────────────────────────────────┘  │
│   ┌──────────┬──────────┬──────────┬──────────┐                    │
│   │ 🐍 后端  │ 🤖 AI    │ 🎨 前端  │ 💾 存储  │                    │
│   │ Python   │ MiMo     │ Live2D   │ JSON     │                    │
│   │ Gradio   │ TTS/ASR  │ PixiJS   │ Memory   │                    │
│   └──────────┴──────────┴──────────┴──────────┘                    │
│   ┌─────────────────────────────────────────────────────────────┐  │
│   │ ✨ 核心特性: 云端架构 │ Live2D │ 9工具 │ 8音色 │ 会话管理 │ Soul │  │
│   └─────────────────────────────────────────────────────────────┘  │
│                         Aivo V6 - 基于小米 MiMo API                 │
│                         Version 6.0 | MIT License                  │
└─────────────────────────────────────────────────────────────────────┘
```

### 7.2 布局说明

#### 顶部横幅
- **项目标题**: 渐变色 "Aivo 数字人 V6"
- **技术栈标签**: Live2D、气泡语音、工具、音色、Soul Memory
- **系统状态**: 绿色指示灯显示 API 连接和 Live2D 就绪状态
- **GitHub 链接**: 直接跳转到项目仓库

#### 左侧主功能区 (scale=3)
- **会话选择器**: 下拉菜单显示所有历史会话，包含第一条消息预览和会话 ID
- **对话窗口**: 480px 高度，支持气泡内嵌音频自动播放
- **文本输入**: 消息输入框 + 发送/新建/清空按钮
- **语音输入**: 录音/上传 + 识别按钮 + 识别结果显示
- **工具面板**: 5 个可折叠面板水平排列
  - 📜 会话管理: 加载、导出、**跨会话搜索**
  - 🎵 音色选择: 8 种音色下拉选择
  - 💡 快速示例: 8 个一键发送按钮
  - 🛠️ 可用工具: 10 个工具快捷按钮
  - 🧠 Soul Memory: 人格、用户、技能、偏好管理

#### 右侧面板 (scale=1)
- **Live2D 数字人**: iframe 隔离渲染，支持点击切换模型
- **统计信息**: 实时更新的对话轮次、响应时间、情感分布

#### 底部信息区
- **技术实现路径**: 6 步流程图（需求分析→部署上线）
- **技术栈详情**: 4 个卡片展示后端、AI、前端、存储技术
- **核心特性**: 8 个特性带发光圆点指示

### 7.3 UI 设计特性

- **深色主题**: 顶部和底部使用深蓝渐变 (#1a1a2e → #0f3460)
- **渐变文字**: 标题使用紫色渐变效果
- **卡片设计**: 圆角 14-24px + 半透明背景 + 边框
- **按钮动画**: 悬停上移 2px + 阴影增强
- **发光效果**: 关键元素使用 box-shadow 发光
- **美化滚动条**: 渐变色滚动条
- **响应式布局**: grid 自动适配不同屏幕尺寸

### 7.4 交互特性

- **一键发送**: 快速示例按钮直接触发对话
- **工具填充**: 工具按钮填充关键词到输入框
- **会话切换**: 左上角快速加载 + 会话管理面板加载
- **跨会话搜索**: 在所有历史会话中搜索关键词
- **实时刷新**: 统计数据每次对话后实时更新
- **会话导出**: 导出当前会话为 JSON 文件

---

## 8. API 集成

### 8.1 MiMo API

**基础配置**:
```python
client = OpenAI(
    api_key=os.getenv("MIMO_API_KEY"),
    base_url="https://token-plan-cn.xiaomimimo.com/v1"
)
```

**使用的模型**:
| 模型 | 用途 | 调用方式 |
|------|------|----------|
| mimo-v2.5-pro | LLM 推理 | chat.completions.create |
| mimo-v2.5-tts | 语音合成 | chat.completions.create (audio) |
| mimo-v2.5-asr | 语音识别 | chat.completions.create (input_audio) |

### 8.2 外部 API

| API | 用途 | 端点 |
|-----|------|------|
| wttr.in | 天气查询 | https://wttr.in/{city}?format=j1 |
| MyMemory | 翻译服务 | https://api.mymemory.translated.net/get |
| DuckDuckGo | 网络搜索 | https://api.duckduckgo.com/ |
| Wikipedia | 维基百科 | https://zh.wikipedia.org/api/ |
| NewsAPI | 新闻资讯 | https://newsapi.org/v2/top-headlines |

---

## 9. 部署与配置

### 9.1 环境要求

- **Python**: 3.8+
- **操作系统**: macOS / Linux / Windows
- **依赖**: 见 requirements.txt

### 9.2 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/Baituhao/Aivo-v2.git
cd Aivo-v2

# 2. 创建虚拟环境
conda create -n aivo python=3.10
conda activate aivo

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 MIMO_API_KEY

# 5. 启动服务
python src/web_ui_v6.py
```

### 9.3 环境变量配置

```bash
# .env 文件
MIMO_API_KEY=your_api_key_here
MIMO_API_BASE=https://token-plan-cn.xiaomimimo.com/v1
```

### 9.4 启动命令

```bash
# Web UI 模式（推荐）
python src/web_ui_v6.py

# 命令行模式
python src/main_v2.py --mode text
python src/main_v2.py --mode voice --duration 5
```

---

## 10. 性能与成本

### 10.1 性能指标

| 指标 | 值 | 说明 |
|------|-----|------|
| LLM 响应时间 | 1-3 秒 | 取决于网络和模型负载 |
| TTS 合成时间 | 0.5-2 秒 | 取决于文本长度 |
| ASR 识别时间 | 0.5-1 秒 | 取决于音频长度 |
| 会话加载时间 | <0.1 秒 | JSON 文件读取 |
| 内存占用 | ~200MB | Python 进程 |

### 10.2 成本估算

**按 1 小时对话计算**:
- ASR: ¥0.36
- LLM: ~¥0.5（估算）
- TTS: ¥0.6
- **总计**: ~¥1.5/小时

**课设 demo 总成本**: < ¥10

---

## 11. 安全与隐私

### 11.1 数据安全

- ✅ **本地存储**: 所有用户数据存储在本地
- ✅ **Git 保护**: 敏感目录已加入 `.gitignore`
- ✅ **无云端上传**: 对话内容不上传第三方服务器
- ✅ **API 密钥保护**: 环境变量存储，不提交到代码库

### 11.2 隐私保护

**排除的目录**:
```gitignore
# 用户数据（隐私保护）
sessions/          # 用户对话历史
memory/            # Soul Memory 用户数据
test_memory/       # 测试数据
node_modules/      # 依赖包
.env               # API 密钥
```

### 11.3 数据管理

- **导出功能**: 用户可导出所有数据
- **删除功能**: 用户可清空所有数据
- **备份建议**: 定期备份 `memory/` 和 `sessions/` 目录

---

## 12. 未来规划

### 12.1 短期计划

- [ ] 支持更多 Live2D 模型
- [ ] 优化 TTS 音频质量
- [ ] 添加更多工具（日历、邮件等）
- [ ] 支持多语言界面

### 12.2 中期计划

- [ ] 支持本地 LLM 模型
- [ ] 添加知识库 RAG 功能
- [ ] 实现多用户支持
- [ ] 移动端适配

### 12.3 长期计划

- [ ] 3D 数字人升级
- [ ] 实时视频通话
- [ ] 情感识别增强
- [ ] 多模态理解（图像、视频）

---

## 附录

### A. 参考资料

- [MiMo API 文档](https://api.xiaomimimo.com)
- [Live2D Cubism SDK](https://www.live2d.com/en/sdk/)
- [Gradio 文档](https://gradio.app/docs/)
- [PixiJS 文档](https://pixijs.com/)

### B. 版本历史

| 版本 | 日期 | 主要更新 |
|------|------|----------|
| V6.0 | 2026-06-21 | Soul Memory、会话管理、统计面板 |
| V5.0 | 2026-06-20 | Live2D 数字人、气泡语音 |
| V4.0 | 2026-06-19 | 工具系统、音色管理 |
| V3.0 | 2026-06-18 | Web UI 重构、语音交互 |
| V2.0 | 2026-06-17 | LLM 工具调用、TTS 情感 |
| V1.0 | 2026-06-16 | 基础对话、ASR/TTS |

### C. 开发团队

- **开发者**: Aivo Team
- **AI 模型**: 小米 MiMo
- **数字人**: Live2D Cubism SDK

---

**文档版本**: V6.0
**最后更新**: 2026-06-21
**状态**: ✅ 生产就绪
