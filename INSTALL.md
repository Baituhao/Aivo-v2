# Aivo V3 安装指南

## 📦 系统要求

- **操作系统**：macOS / Linux / Windows
- **Python版本**：3.8+
- **网络**：稳定的互联网连接
- **API密钥**：小米MiMo API Key

## 🚀 快速安装

### 步骤1：克隆项目

```bash
cd /Users/kk/Aivo-v2
# 或从git克隆
# git clone <repository-url>
```

### 步骤2：安装依赖

**方式1：使用安装脚本（推荐）**
```bash
bash install.sh
```

**方式2：手动安装**
```bash
pip install -r requirements.txt
```

**方式3：逐个安装**
```bash
pip install openai>=1.0.0
pip install python-dotenv==1.0.0
pip install requests==2.31.0
pip install pyaudio>=0.2.13
pip install gradio>=4.0.0
pip install pillow>=10.0.0
```

### 步骤3：配置API密钥

1. 复制环境变量模板：
```bash
cp .env.example .env
```

2. 编辑`.env`文件：
```bash
vim .env
# 或使用其他编辑器
```

3. 填入你的API密钥：
```
MIMO_API_KEY=tp-xxxxxxxxxxxx
MIMO_API_BASE=https://token-plan-cn.xiaomimimo.com/v1
```

### 步骤4：验证安装

运行测试脚本：
```bash
python tests/test_new_tools.py
```

如果看到"✓ 所有工具测试完成"，说明安装成功！

## 🎯 启动系统

### 启动Web界面V3（推荐）

```bash
# 方式1：使用启动脚本
bash run.sh
# 选择选项 1

# 方式2：直接运行
python src/web_ui_v3.py
```

浏览器会自动打开 `http://localhost:7860`

### 启动命令行模式

```bash
# 文本对话
python src/main_v2.py --mode text

# 语音对话
python src/main_v2.py --mode voice --duration 5
```

## ⚠️ 常见问题

### Q1: PyAudio安装失败？

**macOS**:
```bash
brew install portaudio
pip install pyaudio
```

**Ubuntu/Debian**:
```bash
sudo apt-get install portaudio19-dev
pip install pyaudio
```

**Windows**:
```bash
pip install pipwin
pipwin install pyaudio
```

### Q2: Gradio导入失败？

```bash
pip install --upgrade gradio
```

### Q3: API调用401错误？

检查：
1. `.env`文件是否正确配置
2. API_KEY是否以`tp-`开头（token-plan密钥）
3. API_BASE是否为`https://token-plan-cn.xiaomimimo.com/v1`

### Q4: 找不到模块错误？

确保在项目根目录运行：
```bash
cd /Users/kk/Aivo-v2
python src/web_ui_v3.py
```

### Q5: 麦克风权限被拒绝？

**macOS**: 系统偏好设置 → 安全性与隐私 → 麦克风 → 允许浏览器/终端访问

**浏览器**: 浏览器设置 → 隐私和安全 → 网站设置 → 麦克风 → 允许

## 📋 依赖说明

| 包名 | 版本 | 用途 |
|------|------|------|
| openai | >=1.0.0 | MiMo API客户端 |
| python-dotenv | 1.0.0 | 环境变量管理 |
| requests | 2.31.0 | HTTP请求 |
| pyaudio | >=0.2.13 | 录音功能 |
| gradio | >=4.0.0 | Web界面 |
| pillow | >=10.0.0 | 图像处理 |

## 🧪 测试安装

运行完整测试套件：
```bash
# 测试所有工具
bash run.sh
# 选择选项 5 或 6

# 或分别运行
python tests/test_tools.py
python tests/test_new_tools.py
python tests/test_mimo_llm.py
```

## 📖 下一步

安装完成后，参考以下文档：
- [快速开始指南](docs/QUICK_START_V3.md)
- [V3更新日志](docs/CHANGELOG_V3.md)
- [功能总结](docs/V3_SUMMARY.md)

## 💡 小贴士

1. **虚拟环境**（推荐）：
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

2. **国内镜像加速**：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

3. **开发模式**：
```bash
pip install -e .
```

## 📞 获取帮助

- 查看文档：`docs/`目录
- 运行测试：`bash run.sh`（选项5/6）
- 查看日志：启动时添加`PYTHONUNBUFFERED=1`

---

**安装遇到问题？** 参考`docs/PRESENTATION.md`中的Q&A部分
