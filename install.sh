#!/bin/bash
# 一键安装所有依赖并生成表情图片

echo "=== Aivo 依赖安装脚本 ==="
echo ""

# 安装依赖
echo "【步骤1/2】安装Python依赖..."
pip install -q openai python-dotenv requests pyaudio gradio pillow

echo ""
echo "【步骤2/2】生成表情图片..."
python scripts/generate_emotions.py

echo ""
echo "✓ 安装完成！"
echo ""
echo "现在可以运行："
echo "  - 文本对话: python src/main_v2.py --mode text"
echo "  - Web界面: python src/web_ui.py"
