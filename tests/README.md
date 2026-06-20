# 测试脚本说明

## 1. 验证小米MiMo API

### 准备工作

1. 复制环境变量模板：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入你的小米MiMo API密钥和地址

3. 安装依赖：
```bash
pip install -r requirements.txt
```

### 运行测试

```bash
python tests/test_mimo_api.py
```

### 测试内容

- ✓ 基础对话能力
- ✓ Function Calling（工具调用）- **关键能力**
- ✓ 结构化JSON输出 - **关键能力**
- ✓ 流式输出（可选）

### 预期结果

如果 Function Calling 和 JSON输出 都通过，说明MiMo API满足项目需求。

如果不通过，需要切换到备选方案：
- Qwen（通义千问）
- DeepSeek
- Claude

## 2. 后续测试

后续会添加：
- `test_linly_talker.py` - 测试Linly-Talker部署
- `test_dify.py` - 测试Dify工作流
- `test_complete_flow.py` - 测试完整链路
