# Aivo V6 - Soul Memory 使用指南

## 🌟 功能概述

Soul Memory 是 Aivo V6 的灵魂记忆与技能管理系统，可以持久化保存：
- 🎭 **人格设定**：AI 的性格、角色、说话风格
- 👤 **用户画像**：用户的兴趣、习惯、背景信息
- 🛠️ **技能系统**：AI 掌握的知识领域和能力
- ⚙️ **偏好设置**：语言、回复风格、表情使用等

## 📂 文件结构

```
Aivo-v2/
├── memory/                    # Soul Memory 存储目录
│   ├── personality.json       # 人格设定
│   ├── user_profile.json      # 用户画像
│   ├── skills.json            # 技能列表
│   └── preferences.json       # 偏好设置
├── sessions/                  # 会话历史目录
│   └── session_*.json         # 各个会话文件
└── src/
    ├── soul_memory.py         # Soul Memory 核心模块
    └── web_ui_v6.py           # 集成 UI 界面
```

## 🎯 主要功能

### 1. 人格设定 (🎭)

定义 AI 的基本人格特征：

- **名称**：AI 的名字（如 "Aivo"）
- **角色**：AI 的定位（如 "AI数字人助手"）
- **特质**：性格特点（如 "友好热情、专业可靠"）
- **说话风格**：表达方式（如 "温暖亲切，乐于助人"）

**使用场景**：
- 为不同场景定制不同的 AI 人格
- 企业客服、教育助手、生活伴侣等不同角色

### 2. 用户画像 (👤)

记录用户的个性化信息：

- **用户名称**：称呼用户
- **兴趣爱好**：用户感兴趣的话题
- **使用习惯**：用户的使用偏好
- **背景信息**：职业、专业等背景

**使用场景**：
- 个性化推荐内容
- 根据用户背景调整回复深度
- 记住用户偏好提供更好服务

### 3. 技能系统 (🛠️)

管理 AI 的能力范围：

**默认知识领域**：
- 通用对话
- 天气查询
- 信息搜索
- 文本翻译
- 数学计算

**自定义技能**：
- 可添加任意领域的技能
- 设置技能等级（初级/中级/专家）
- 启用/禁用特定技能

**使用场景**：
- 专业领域定制（医疗、法律、教育等）
- 控制 AI 的回答范围
- 技能升级管理

### 4. 偏好设置 (⚙️)

调整 AI 的行为方式：

- **语言**：中文、English、日本語
- **回复风格**：简洁、适中、详细
- **表情符号**：少、适中、多
- **正式程度**：随意、友好、正式

**使用场景**：
- 适配不同用户群体
- 商务场景 vs 休闲场景
- 快速问答 vs 深度讨论

## 💻 Web UI 操作

### 访问 Soul Memory 面板

1. 启动 Aivo V6：`python src/web_ui_v6.py`
2. 在右侧栏找到 **🧠 Soul Memory** 面板
3. 点击展开，查看 4 个标签页

### 编辑人格设定

```
🎭 人格 标签：
1. 修改名称、角色、特质、说话风格
2. 点击 "💾 保存人格设定"
3. 立即生效，所有新对话将使用新设定
```

### 管理用户画像

```
👤 用户 标签：
1. 填写用户名称和背景信息
2. 添加兴趣爱好（逗号分隔）
3. 记录使用习惯
4. 点击 "💾 保存用户画像"
```

### 添加技能

```
🛠️ 技能 标签：
1. 输入新技能名称（如 "Python编程"）
2. 选择技能等级
3. 点击 "➕ 添加技能"
4. 使用 "🔄 刷新列表" 查看更新
```

### 调整偏好设置

```
⚙️ 偏好 标签：
1. 从下拉菜单选择各项偏好
2. 点击 "💾 保存偏好设置"
3. 新设置将在下次对话中生效
```

## 📥 导入导出

### 导出记忆

```python
# Web UI 中点击 "💾 导出记忆"
# 文件保存到: memory/soul_memory_export_YYYYMMDD_HHMMSS.json
```

### 导入记忆

1. 将导出的 JSON 文件复制到 `memory/` 目录
2. 重命名为对应的文件名：
   - `personality.json`
   - `user_profile.json`
   - `skills.json`
   - `preferences.json`
3. 重启 Aivo V6，自动加载新记忆

## 🔧 编程接口

### 基本使用

```python
from pathlib import Path
from soul_memory import SoulMemory

# 初始化
memory_dir = Path("./memory")
soul = SoulMemory(memory_dir)

# 更新人格
soul.update_personality(
    name="专业助手",
    role="技术顾问",
    traits=["专业", "严谨", "高效"],
    speaking_style="简明扼要"
)

# 添加用户兴趣
soul.add_user_interest("人工智能")
soul.add_user_habit("晚上工作")

# 添加技能
soul.add_skill("机器学习", level="expert", enabled=True)

# 更新偏好
soul.update_preferences(
    language="中文",
    response_style="详细",
    formality="正式"
)

# 获取摘要
print(soul.get_summary())

# 导出所有记忆
soul.export_all(Path("./backup.json"))
```

## 🎯 使用建议

### 场景 1：企业客服

```json
{
  "personality": {
    "name": "小助",
    "role": "企业客服助手",
    "traits": ["专业", "耐心", "热情"],
    "speaking_style": "礼貌正式，解决问题"
  },
  "preferences": {
    "response_style": "详细",
    "formality": "正式",
    "emoji_usage": "少"
  }
}
```

### 场景 2：教育助手

```json
{
  "personality": {
    "name": "小老师",
    "role": "在线教育助手",
    "traits": ["耐心", "鼓励", "启发"],
    "speaking_style": "循循善诱，深入浅出"
  },
  "preferences": {
    "response_style": "详细",
    "formality": "友好",
    "emoji_usage": "适中"
  }
}
```

### 场景 3：生活伴侣

```json
{
  "personality": {
    "name": "Aivo",
    "role": "AI生活伴侣",
    "traits": ["温暖", "幽默", "善解人意"],
    "speaking_style": "轻松愉快，亲切自然"
  },
  "preferences": {
    "response_style": "适中",
    "formality": "随意",
    "emoji_usage": "多"
  }
}
```

## 📊 数据持久化

- **自动保存**：所有修改立即写入磁盘
- **启动加载**：程序启动时自动加载最新数据
- **跨会话保持**：重启后记忆依然存在
- **备份安全**：支持导出导入，便于备份和迁移

## 🔒 隐私与安全

- 所有数据存储在本地
- 不上传到云端服务器
- 用户完全控制数据
- 可随时删除或修改

## 📞 技术支持

如有问题，请检查：
1. `memory/` 目录权限是否正常
2. JSON 文件格式是否正确
3. 查看控制台错误日志

---

**Aivo V6 - 更智能的数字人助手** 🎀
